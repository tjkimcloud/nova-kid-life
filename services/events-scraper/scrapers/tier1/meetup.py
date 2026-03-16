"""
Meetup.com scraper — Northern Virginia family events + Pokémon TCG groups.

Uses the Meetup REST API v3 with OAuth2 client credentials.

Setup (one-time):
  1. Create a Meetup account at meetup.com
  2. Register an OAuth consumer at: https://www.meetup.com/api/oauth/list/
  3. Set MEETUP_CLIENT_ID and MEETUP_CLIENT_SECRET in .env

What it scrapes:
  - Family/kids events within 30 miles of Fairfax, VA
  - Parent group events (moms, dads, playgroups)
  - Pokémon TCG meetups (tagged section='pokemon')
  - Toddler/preschool playgroups
  - Outdoor/nature family meetups
"""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone

import httpx

from scrapers.base import BaseScraper
from scrapers.models import EventType, RawEvent

logger = logging.getLogger(__name__)

# NoVa center coordinates (Fairfax City area)
_LAT    = 38.8462
_LON    = -77.3064
_RADIUS = 30  # miles

_TOKEN_URL = "https://secure.meetup.com/oauth2/access"
_EVENTS_URL = "https://api.meetup.com/find/events"

# Keyword groups → determines section and tags
_FAMILY_KEYWORDS = [
    "kids", "family", "children", "toddler", "preschool", "baby",
    "parent", "moms", "dads", "playgroup", "storytime", "nursery",
    "infant", "elementary", "youth", "teen", "tween", "homeschool",
    "mommy", "daddy", "little ones", "play date", "playdate",
]

_POKEMON_KEYWORDS = [
    "pokemon", "pokémon", "tcg", "trading card", "card game",
    "pokebeach", "booster", "prerelease",
]

_NATURE_TAGS     = ["outdoor", "nature", "hiking", "park", "trail"]
_SPORTS_TAGS     = ["sports", "soccer", "swim", "tennis", "fitness"]
_ARTS_TAGS       = ["art", "craft", "music", "theater", "dance"]
_STEM_TAGS       = ["stem", "science", "technology", "coding", "robotics"]


def _get_token() -> str | None:
    """Fetch OAuth2 client credentials token."""
    client_id     = os.getenv("MEETUP_CLIENT_ID", "")
    client_secret = os.getenv("MEETUP_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        logger.warning("MEETUP_CLIENT_ID / MEETUP_CLIENT_SECRET not set — skipping Meetup")
        return None

    try:
        resp = httpx.post(
            _TOKEN_URL,
            data={
                "grant_type":    "client_credentials",
                "client_id":     client_id,
                "client_secret": client_secret,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("access_token")
    except Exception as exc:
        logger.warning("Meetup OAuth failed: %s", exc)
        return None


def _classify(title: str, description: str) -> tuple[str, list[str], str]:
    """Return (event_type_value, tags, section)."""
    text = (title + " " + description).lower()

    # Pokémon check first
    if any(kw in text for kw in _POKEMON_KEYWORDS):
        return EventType.POKEMON_TCG.value, ["pokemon", "tcg", "meetup"], "pokemon"

    # Build tag list
    tags = ["meetup", "community"]
    for kw in _NATURE_TAGS:
        if kw in text:
            tags.append(kw)
    for kw in _SPORTS_TAGS:
        if kw in text:
            tags.append(kw)
    for kw in _ARTS_TAGS:
        if kw in text:
            tags.append(kw)
    for kw in _STEM_TAGS:
        if kw in text:
            tags.append(kw)

    return EventType.EVENT.value, tags, "main"


def _make_slug(event_id: str, title: str) -> str:
    safe = "".join(c if c.isalnum() or c == "-" else "-" for c in title.lower())
    safe = "-".join(p for p in safe.split("-") if p)
    return f"meetup-{safe[:50]}-{event_id}"


class MeetupScraper(BaseScraper):
    """
    Scrapes Meetup.com for Northern Virginia family events.

    Queries multiple keyword sets to maximize coverage, deduplicates by event ID.
    """

    source_name = "meetup_nova"

    # Search queries — each runs as a separate API call
    _QUERIES = [
        "kids family",
        "toddler playgroup",
        "parent moms",
        "homeschool",
        "youth teen",
        "pokemon trading card",
    ]

    def scrape(self) -> list[RawEvent]:
        token = _get_token()
        if not token:
            return []

        events: dict[str, RawEvent] = {}  # keyed by Meetup event ID (dedup)

        for query in self._QUERIES:
            try:
                batch = self._search(token, query)
                for evt in batch:
                    if evt.slug not in events:
                        events[evt.slug] = evt
            except Exception as exc:
                logger.warning("Meetup query '%s' failed: %s", query, exc)

        results = list(events.values())
        logger.info("MeetupScraper: %d events found", len(results))
        return results

    def _search(self, token: str, text: str) -> list[RawEvent]:
        resp = httpx.get(
            _EVENTS_URL,
            params={
                "lat":      _LAT,
                "lon":      _LON,
                "radius":   _RADIUS,
                "text":     text,
                "page":     50,  # results per query
                "order":    "time",
                "fields":   "featured_photo,group_photo",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        events = []
        for item in data:
            # Filter: only include events that match family/pokemon keywords
            title       = item.get("name", "")
            description = item.get("description", "")
            full_text   = (title + " " + description).lower()

            is_family  = any(kw in full_text for kw in _FAMILY_KEYWORDS)
            is_pokemon = any(kw in full_text for kw in _POKEMON_KEYWORDS)

            if not is_family and not is_pokemon:
                continue

            events.append(self._to_raw_event(item))

        return events

    def _to_raw_event(self, item: dict) -> RawEvent:
        title       = item.get("name", "Meetup Event")
        description = item.get("description", "")
        event_id    = str(item.get("id", ""))

        # Timing
        time_ms  = item.get("time", 0)
        start_at = (
            datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc).isoformat()
            if time_ms else None
        )

        # Location
        venue       = item.get("venue", {})
        loc_name    = venue.get("name") or item.get("group", {}).get("name", "")
        loc_address = ", ".join(filter(None, [
            venue.get("address_1"),
            venue.get("city"),
            venue.get("state"),
        ]))

        lat = venue.get("lat") or item.get("group", {}).get("lat")
        lng = venue.get("lon") or item.get("group", {}).get("lon")

        # Cost
        fee      = item.get("fee", {})
        is_free  = not bool(fee.get("amount"))
        cost_desc = f"${fee['amount']} {fee.get('currency', '')}" if fee.get("amount") else "Free"

        # Classification
        evt_type, tags, section = _classify(title, description)

        # Image
        photo    = item.get("featured_photo") or item.get("group", {}).get("group_photo") or {}
        image_url = photo.get("photo_link", "")

        source_url = item.get("link", f"https://www.meetup.com/events/{event_id}/")

        return RawEvent(
            title            = title,
            description      = description[:2000],
            start_at         = start_at,
            location_name    = loc_name,
            location_address = loc_address,
            source_url       = source_url,
            source_name      = self.source_name,
            image_url        = image_url,
            tags             = tags,
            event_type       = EventType(evt_type),
            section          = section,
            is_free          = is_free,
            cost_description = cost_desc,
            slug             = _make_slug(event_id, title),
            lat              = float(lat) if lat else None,
            lng              = float(lng) if lng else None,
        )
