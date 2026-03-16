"""
Pokémon TCG Product Drops Scraper

Tracks upcoming set releases and where to buy in Northern Virginia.

Sources:
  1. pokemon.com/us/pokemon-tcg/product-releases/ — official release calendar
  2. pokebeach.com — earliest reliable release date leaks + confirmed dates
  3. Static NoVa retailer matrix — curated store list with product links

Strategy:
  - Scrape release dates and set details (AI extractor on both sites)
  - Pair each release with the full NoVa retailer matrix
  - Store as event_type=product_drop, section=pokemon
  - image_url left None → image-gen picks up the official set artwork prompt
  - No real-time inventory (fragile) — link to each retailer's search page instead
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone

import httpx
from openai import OpenAI

from scrapers.base import BaseScraper
from scrapers.models import EventType, RawEvent

logger = logging.getLogger(__name__)


# ── NoVa Retailer Matrix ───────────────────────────────────────────────────────
# Each entry: name, type (big_box | specialty | online), store_locator or product search URL,
# notes about their TCG stock patterns.

NOVA_RETAILERS: list[dict] = [
    # ── Big Box ────────────────────────────────────────────────────────────────
    {
        "name":    "Target",
        "type":    "big_box",
        "search_url": "https://www.target.com/s?searchTerm=pokemon+tcg",
        "locator": "https://www.target.com/store-locator/find-stores",
        "nova_locations": [
            "Fairfax (Fair Lakes)", "Reston", "Herndon", "Sterling",
            "Leesburg", "Manassas", "Alexandria (Potomac Yard)",
            "Arlington (Clarendon)", "Springfield", "Falls Church",
        ],
        "notes": "Carries booster packs, ETBs, and tins. Stock often drops early on release morning.",
    },
    {
        "name":    "Walmart",
        "type":    "big_box",
        "search_url": "https://www.walmart.com/search?q=pokemon+tcg",
        "locator": "https://www.walmart.com/store/finder",
        "nova_locations": [
            "Manassas", "Woodbridge", "Chantilly", "Leesburg",
            "Herndon", "Falls Church", "Alexandria",
        ],
        "notes": "Competitive pricing on booster boxes. Often restocks Thursday nights.",
    },
    {
        "name":    "GameStop",
        "type":    "big_box",
        "search_url": "https://www.gamestop.com/search#q=pokemon+tcg&t=All",
        "locator": "https://www.gamestop.com/store-locator",
        "nova_locations": [
            "Fair Oaks Mall (Fairfax)", "Dulles Town Center (Sterling)",
            "Potomac Mills (Woodbridge)", "Tysons Corner Center",
            "Manassas Mall", "Springfield Town Center",
            "Reston Town Center", "Leesburg Corner Premium Outlets",
        ],
        "notes": "Gets exclusive Pokémon Center collector sets. Does midnight/launch-day events for major releases.",
    },
    {
        "name":    "Best Buy",
        "type":    "big_box",
        "search_url": "https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+tcg",
        "locator": "https://stores.bestbuy.com/",
        "nova_locations": [
            "Fairfax (Fair Lakes)", "Dulles (Sterling)",
            "Tysons Corner", "Springfield",
        ],
        "notes": "Carries ETBs and premium collections. Often has online ship-to-store on release day.",
    },
    {
        "name":    "Costco",
        "type":    "big_box",
        "search_url": "https://www.costco.com/CatalogSearch?keyword=pokemon",
        "locator": "https://www.costco.com/warehouse-locations",
        "nova_locations": [
            "Chantilly", "Fairfax", "Tysons Corner (McLean)",
            "Sterling", "Woodbridge",
        ],
        "notes": "Best value — carries 3-pack booster bundles and elite trainer box bundles, often below MSRP. Seasonal and major sets only.",
    },
    {
        "name":    "Sam's Club",
        "type":    "big_box",
        "search_url": "https://www.samsclub.com/s/pokemon",
        "locator": "https://www.samsclub.com/club-finder",
        "nova_locations": [
            "Chantilly", "Woodbridge",
        ],
        "notes": "Similar to Costco — bundle value packs at competitive prices for major sets.",
    },
    {
        "name":    "Five Below",
        "type":    "big_box",
        "search_url": "https://www.fivebelow.com/content/search?q=pokemon",
        "locator": "https://stores.fivebelow.com/",
        "nova_locations": [
            "Multiple NoVa locations (Fairfax, Sterling, Manassas, Woodbridge, Leesburg)",
        ],
        "notes": "Carries booster packs at $5 price point. Great for kids' allowance budget. Stocks quickly.",
    },
    {
        "name":    "Books-A-Million",
        "type":    "big_box",
        "search_url": "https://www.booksamillion.com/search?query=pokemon+tcg",
        "locator": "https://www.booksamillion.com/stores",
        "nova_locations": [
            "Manassas", "Sterling (Dulles Town Center)",
        ],
        "notes": "Underrated TCG source. Carries packs and ETBs with occasional 20% off coupons.",
    },
    # ── Specialty / Local Game Stores ─────────────────────────────────────────
    {
        "name":    "Nerd Rage Gaming",
        "type":    "specialty",
        "search_url": "https://www.nerdragegaming.com/",
        "locator": "https://www.nerdragegaming.com/pages/locations",
        "nova_locations": [
            "Manassas (9580 Center St)", "Chantilly (forthcoming)",
        ],
        "notes": "Largest TCG-focused LGS in NoVa. Hosts weekly Pokémon League, prerelease events, and regional qualifiers. Preorder through their site for guaranteed prerelease allocation.",
    },
    {
        "name":    "Battlegrounds Games & Hobbies",
        "type":    "specialty",
        "search_url": "https://battlegroundsgames.com/pokemon/",
        "locator": "https://battlegroundsgames.com/contact/",
        "nova_locations": [
            "Leesburg (537 E Market St)", "Ashburn",
        ],
        "notes": "Strong Pokémon TCG community in Loudoun County. Weekly leagues and prereleases. Buy singles here.",
    },
    {
        "name":    "The Game Parlor",
        "type":    "specialty",
        "search_url": "https://thegameparlor.com/",
        "locator": "https://thegameparlor.com/contact",
        "nova_locations": [
            "Chantilly (14677 Lee Hwy)",
        ],
        "notes": "Friendly family atmosphere. Good for new players. Hosts intro Pokémon League nights.",
    },
    {
        "name":    "Collector's Cache",
        "type":    "specialty",
        "search_url": "https://collectorscachegames.com/pokemon/",
        "locator": "https://collectorscachegames.com/contact/",
        "nova_locations": [
            "Alexandria (6317 Seven Corners Center)",
        ],
        "notes": "Good singles inventory and sealed product. Hosts small locals and league events.",
    },
    {
        "name":    "Dream Wizards",
        "type":    "specialty",
        "search_url": "https://www.dreamwizards.com/",
        "locator": "https://www.dreamwizards.com/contact",
        "nova_locations": [
            "Rockville, MD (12420 Wilkins Ave) — 10 min from NoVa border",
        ],
        "notes": "One of the DC metro's oldest LGS. Large TCG section, active Pokémon league, prereleases.",
    },
    # ── Online with Local Pickup ───────────────────────────────────────────────
    {
        "name":    "TCGPlayer",
        "type":    "online",
        "search_url": "https://www.tcgplayer.com/search/pokemon/product",
        "locator": None,
        "nova_locations": [],
        "notes": "Best prices on singles. Ships fast. Use for building decks or completing sets.",
    },
    {
        "name":    "Pokémon Center (Official)",
        "type":    "online",
        "search_url": "https://www.pokemoncenter.com/category/trading-card-game",
        "locator": None,
        "nova_locations": [],
        "notes": "Official store. Exclusive sets, promo cards, and collector items. Ships to NoVa.",
    },
]


# ── Sources ────────────────────────────────────────────────────────────────────

_SOURCES = [
    {
        "label": "Pokemon.com release calendar",
        "url":   "https://www.pokemon.com/us/pokemon-tcg/pokemon-tcg-expansions/",
    },
    {
        "label": "PokéBeach TCG news",
        "url":   "https://www.pokebeach.com/category/tcg-releases",
    },
]


def _make_drop_slug(set_name: str, release_date: str) -> str:
    raw = f"pokemon-drop-{set_name}-{release_date}".lower()
    safe = "".join(c if c.isalnum() or c == "-" else "-" for c in raw)
    safe = "-".join(p for p in safe.split("-") if p)
    h = hashlib.md5(raw.encode()).hexdigest()[:6]
    return f"{safe[:60]}-{h}"


def _retailer_summary() -> str:
    """Build a markdown-friendly summary of NoVa retailers for event description."""
    big_box   = [r for r in NOVA_RETAILERS if r["type"] == "big_box"]
    specialty = [r for r in NOVA_RETAILERS if r["type"] == "specialty"]
    online    = [r for r in NOVA_RETAILERS if r["type"] == "online"]

    lines = ["**Where to buy in Northern Virginia:**\n"]
    lines.append("*Big Box Stores:* " + ", ".join(r["name"] for r in big_box))
    lines.append("*Local Game Stores:* " + ", ".join(r["name"] for r in specialty))
    lines.append("*Online:* " + ", ".join(r["name"] for r in online))
    return "\n".join(lines)


class PokemonDropsScraper(BaseScraper):
    """
    Scrapes upcoming Pokémon TCG set release dates and pairs them
    with the NoVa retailer matrix.
    """

    source_name = "pokemon_tcg_drops"

    def scrape(self) -> list[RawEvent]:
        drops: list[RawEvent] = []
        seen: set[str] = set()

        for source in _SOURCES:
            try:
                new_drops = self._scrape_source(source["url"], source["label"])
                for drop in new_drops:
                    if drop.title not in seen:
                        seen.add(drop.title)
                        drops.append(drop)
            except Exception as exc:
                logger.warning("Drop scrape failed for %s: %s", source["label"], exc)

        logger.info("PokemonDropsScraper: %d upcoming drops found", len(drops))
        return drops

    def _scrape_source(self, url: str, label: str) -> list[RawEvent]:
        """Fetch + AI extract release calendar entries."""
        try:
            resp = httpx.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NovaKidLife/1.0)"},
                timeout=15,
                follow_redirects=True,
            )
            resp.raise_for_status()
            html = self._clean_html(resp.text)
        except Exception as exc:
            logger.debug("Fetch failed %s: %s", url, exc)
            return []

        return self._ai_extract_drops(html, label)

    def _ai_extract_drops(self, html: str, source_label: str) -> list[RawEvent]:
        """Extract Pokémon TCG set releases from HTML via gpt-4o-mini."""
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        system_prompt = (
            "You extract Pokémon TCG product release information from HTML content. "
            "Return a JSON object with key 'releases' containing an array. "
            "Each release object must have: "
            "set_name (string), release_date (ISO 8601 date or descriptive string), "
            "msrp (string or null, e.g. '$4.99 per pack'), "
            "card_count (string or null, e.g. '198 cards'), "
            "product_types (array of strings, e.g. ['Booster Pack', 'Elite Trainer Box', 'Booster Bundle']), "
            "description (string, 1-2 sentences about the set), "
            "image_url (string or null — official set artwork URL if present). "
            "Only include future or very recent releases (within last 60 days). "
            "Return raw JSON only."
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
            data = json.loads(response.choices[0].message.content)
            releases = data.get("releases", [])
            if not isinstance(releases, list):
                return []

            return [self._to_raw_event(r) for r in releases if r.get("set_name")]

        except Exception as exc:
            logger.warning("AI extraction failed for %s: %s", source_label, exc)
            return []

    def _to_raw_event(self, data: dict) -> RawEvent:
        set_name     = data.get("set_name", "New Pokémon TCG Set")
        release_date = data.get("release_date", "")
        msrp         = data.get("msrp", "")
        card_count   = data.get("card_count", "")
        products     = data.get("product_types", [])
        description  = data.get("description", "")

        # Build rich description with retailer matrix
        full_description = f"{description}\n\n"
        if msrp:
            full_description += f"**MSRP:** {msrp}  \n"
        if card_count:
            full_description += f"**Cards in set:** {card_count}  \n"
        if products:
            full_description += f"**Available as:** {', '.join(products)}  \n"
        full_description += "\n" + _retailer_summary()

        return RawEvent(
            title         = f"New Pokémon Set: {set_name}",
            description   = full_description,
            start_at      = self._parse_date(release_date),
            location_name = "Northern Virginia",
            location_address = None,
            source_url    = "https://www.pokemon.com/us/pokemon-tcg/pokemon-tcg-expansions/",
            image_url     = data.get("image_url"),
            tags          = ["pokemon", "tcg", "product-drop", "new-set", "trading-cards"],
            event_type    = EventType.PRODUCT_DROP,
            section       = "pokemon",
            brand         = "The Pokémon Company",
            slug          = _make_drop_slug(set_name, release_date),
        )

    def _parse_date(self, date_str: str) -> str | None:
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%B %Y"):
            try:
                dt = datetime.strptime(date_str.strip()[:20], fmt)
                return dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                continue
        return None


def get_nova_retailers() -> list[dict]:
    """Return the full NoVa retailer matrix (used by the frontend /pokemon page)."""
    return NOVA_RETAILERS
