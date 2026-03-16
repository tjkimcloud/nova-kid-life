"""
Pokémon TCG Events Scraper — Northern Virginia

Sources:
  1. Play! Pokémon official event locator (zip code search API)
  2. Nerd Rage Gaming (Manassas) — major NoVa LGS
  3. Battlegrounds Games & Hobbies (Leesburg/Ashburn)
  4. The Game Parlor (Chantilly)
  5. Collector's Cache (Alexandria)
  6. AI extractor fallback for any LGS added to config

Event types captured:
  - Weekly League (recurring)
  - Prerelease Tournament (every ~3 months per new set)
  - Regional Championship
  - Local Tournament / League Challenge
  - Pokemon Go Raid Day (bonus engagement)
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone

import httpx

from scrapers.base import BaseScraper
from scrapers.models import EventType, RawEvent

logger = logging.getLogger(__name__)

# Northern Virginia zip codes to search (covers Fairfax, Loudoun, Arlington, Prince William)
_NOVA_ZIPS = [
    "20109",  # Manassas
    "20165",  # Sterling / Ashburn
    "20170",  # Herndon
    "20190",  # Reston
    "22003",  # Annandale
    "22015",  # Burke
    "22030",  # Fairfax
    "22031",  # Fairfax / Falls Church
    "22033",  # Fairfax
    "22101",  # McLean
    "22150",  # Springfield
    "22182",  # Vienna / Tysons
    "22201",  # Arlington
    "20175",  # Leesburg
    "20151",  # Chantilly
]

# Play! Pokémon event locator API
_PLAY_POKEMON_API = "https://www.pokemon.com/us/play-pokemon/find-a-pokemon-league/"
_PLAY_POKEMON_EVENTS_API = "https://www.pokemon.com/us/play-pokemon/where-to-play/"

# Known NoVa LGS that host regular TCG events
_NOVA_LGS: list[dict] = [
    {
        "name": "Nerd Rage Gaming",
        "url": "https://www.nerdragegaming.com/events",
        "location": "Manassas, VA",
        "zip": "20109",
    },
    {
        "name": "Battlegrounds Games & Hobbies",
        "url": "https://battlegroundsgames.com/events/",
        "location": "Leesburg, VA",
        "zip": "20175",
    },
    {
        "name": "The Game Parlor",
        "url": "https://thegameparlor.com/events",
        "location": "Chantilly, VA",
        "zip": "22151",
    },
    {
        "name": "Collector's Cache",
        "url": "https://collectorscachegames.com/events/",
        "location": "Alexandria, VA",
        "zip": "22314",
    },
    {
        "name": "Dream Wizards",
        "url": "https://www.dreamwizards.com/events",
        "location": "Rockville, MD",
        "zip": "20850",
    },
]

# Tournament format keywords for tagging
_FORMAT_KEYWORDS = {
    "prerelease":   ["prerelease", "pre-release", "pre release"],
    "regional":     ["regional", "championship", "special championship"],
    "league":       ["league", "league challenge", "weekly"],
    "tournament":   ["tournament", "local tournament", "open"],
    "raid":         ["raid", "pokemon go", "community day"],
}


def _detect_format(title: str, description: str) -> list[str]:
    """Return format tags from event title/description."""
    text = (title + " " + description).lower()
    tags = ["pokemon", "tcg", "trading-cards"]
    for fmt, keywords in _FORMAT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            tags.append(fmt)
    return tags


def _make_slug(title: str, location: str, date_str: str) -> str:
    raw = f"pokemon-{title}-{location}-{date_str}".lower()
    safe = "".join(c if c.isalnum() or c == "-" else "-" for c in raw)
    safe = "-".join(p for p in safe.split("-") if p)
    h = hashlib.md5(raw.encode()).hexdigest()[:6]
    return f"{safe[:60]}-{h}"


class PokemonEventsScraper(BaseScraper):
    """
    Scrapes Pokémon TCG events for Northern Virginia.

    Cascade:
      1. Play! Pokémon event locator (official, most complete)
      2. Individual LGS websites via AI extractor
    """

    source_name = "pokemon_tcg_events"

    def scrape(self) -> list[RawEvent]:
        events: list[RawEvent] = []

        # 1. Official Play! Pokémon locator
        events.extend(self._scrape_play_pokemon())

        # 2. Individual LGS sites
        for lgs in _NOVA_LGS:
            try:
                events.extend(self._scrape_lgs(lgs))
            except Exception as exc:
                logger.warning("LGS scrape failed for %s: %s", lgs["name"], exc)

        logger.info("PokemonEventsScraper: %d events found", len(events))
        return events

    def _scrape_play_pokemon(self) -> list[RawEvent]:
        """Query Play! Pokémon event locator for NoVa zip codes."""
        events: list[RawEvent] = []
        seen_ids: set[str] = set()

        for zip_code in _NOVA_ZIPS[:6]:  # Sample key zips — full list would hit rate limits
            try:
                # Play! Pokémon uses a search endpoint — get the HTML and extract via AI
                html = self._fetch_html(
                    f"https://www.pokemon.com/us/play-pokemon/where-to-play/?zipCode={zip_code}&distance=25"
                )
                if not html:
                    continue

                extracted = self._ai_extract_pokemon_events(html, f"Pokemon.com events near {zip_code}")
                for evt in extracted:
                    key = evt.source_url or evt.title
                    if key not in seen_ids:
                        seen_ids.add(key)
                        events.append(evt)

            except Exception as exc:
                logger.debug("Play! Pokemon zip %s failed: %s", zip_code, exc)

        return events

    def _scrape_lgs(self, lgs: dict) -> list[RawEvent]:
        """Scrape a local game store's events page via AI extractor."""
        html = self._fetch_html(lgs["url"])
        if not html:
            return []

        extracted = self._ai_extract_pokemon_events(html, lgs["name"])
        # Patch location info onto any events that didn't get it
        for evt in extracted:
            if not evt.location_name:
                evt.location_name = lgs["name"]
            if not evt.location_address:
                evt.location_address = lgs["location"]

        return extracted

    def _fetch_html(self, url: str) -> str | None:
        """Fetch and clean HTML from a URL."""
        try:
            resp = httpx.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NovaKidLife/1.0)"},
                timeout=15,
                follow_redirects=True,
            )
            resp.raise_for_status()
            return self._clean_html(resp.text)
        except Exception as exc:
            logger.debug("Fetch failed for %s: %s", url, exc)
            return None

    def _ai_extract_pokemon_events(self, html: str, source_label: str) -> list[RawEvent]:
        """Use gpt-4o-mini to extract Pokémon TCG events from cleaned HTML."""
        import os
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        system_prompt = (
            "You extract Pokémon TCG events from HTML content. "
            "Return a JSON array of event objects. Each object must have: "
            "title (string), date (ISO 8601 or descriptive string), "
            "time (string or null), location_name (string), "
            "location_address (string or null), description (string), "
            "url (string or null), format (one of: league, prerelease, regional, tournament, raid, other). "
            "Only include Pokémon TCG events. Return [] if none found. Return raw JSON only."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Source: {source_label}\n\nHTML:\n{html[:6000]}"},
                ],
                max_tokens=2000,
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            raw_events = data.get("events", data) if isinstance(data, dict) else data
            if not isinstance(raw_events, list):
                return []

            return [self._to_raw_event(e, source_label) for e in raw_events if e.get("title")]

        except Exception as exc:
            logger.warning("AI extraction failed for %s: %s", source_label, exc)
            return []

    def _to_raw_event(self, data: dict, source_label: str) -> RawEvent:
        title       = data.get("title", "Pokémon TCG Event")
        location    = data.get("location_name", "Northern Virginia")
        date_str    = data.get("date", "")
        fmt         = data.get("format", "tournament")
        description = data.get("description", "")

        tags = _detect_format(title, description)
        if fmt and fmt not in tags:
            tags.append(fmt)

        return RawEvent(
            title         = title,
            description   = description,
            start_at      = self._parse_date(date_str),
            location_name = location,
            location_address = data.get("location_address"),
            source_url    = data.get("url") or f"https://www.pokemon.com/us/play-pokemon/",
            image_url     = None,
            tags          = tags,
            event_type    = EventType.EVENT,
            section       = "pokemon",
            slug          = _make_slug(title, location, date_str),
        )

    def _parse_date(self, date_str: str) -> str | None:
        """Best-effort ISO date parse — return None if unparseable."""
        if not date_str:
            return None
        try:
            # Try common formats
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
                try:
                    dt = datetime.strptime(date_str.strip()[:20], fmt)
                    return dt.replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    continue
        except Exception:
            pass
        return None
