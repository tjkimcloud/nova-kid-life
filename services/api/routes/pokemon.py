"""
Pokémon TCG section endpoints:
  GET /pokemon/events    — leagues, prereleases, tournaments
  GET /pokemon/drops     — upcoming set releases with retailer matrix
  GET /pokemon/retailers — full NoVa retailer matrix
"""
from __future__ import annotations

from datetime import datetime, timezone

from db import get_client
from models import event_to_response, paginated
from router import ok, error


# ── GET /pokemon/events ───────────────────────────────────────────────────────

def pokemon_events(event: dict, ctx) -> dict:
    qs     = event.get("queryStringParameters") or {}
    origin = event.get("_origin")
    limit  = min(int(qs.get("limit", 20)), 100)
    offset = int(qs.get("offset", 0))
    fmt    = qs.get("format")   # league | prerelease | regional | tournament

    db = get_client()

    now = datetime.now(timezone.utc).isoformat()

    count_q = (
        db.table("events")
        .select("id", count="exact")
        .eq("status", "published")
        .eq("section", "pokemon")
        .eq("event_type", "pokemon_tcg")
        .gte("start_at", now)
    )

    data_q = (
        db.table("events")
        .select(
            "id, slug, title, full_description, start_at, end_at, "
            "venue_name, address, lat, lng, "
            "event_type, tags, is_free, cost_description, "
            "registration_url, image_url, image_url_sm, "
            "image_alt, image_blurhash, image_width, image_height"
        )
        .eq("status", "published")
        .eq("section", "pokemon")
        .eq("event_type", "pokemon_tcg")
        .gte("start_at", now)
        .order("start_at", desc=False)
        .range(offset, offset + limit - 1)
    )

    # Filter by format tag (league, prerelease, regional, tournament)
    if fmt:
        count_q = count_q.contains("tags", [fmt])
        data_q  = data_q.contains("tags", [fmt])

    count_resp = count_q.execute()
    data_resp  = data_q.execute()

    total = count_resp.count or 0
    items = [event_to_response(r) for r in (data_resp.data or [])]

    return ok(paginated(items, total, limit, offset), origin=origin)


# ── GET /pokemon/drops ────────────────────────────────────────────────────────

def pokemon_drops(event: dict, ctx) -> dict:
    """Upcoming Pokémon TCG set releases with NoVa retailer matrix embedded in description."""
    qs     = event.get("queryStringParameters") or {}
    origin = event.get("_origin")
    limit  = min(int(qs.get("limit", 10)), 20)
    offset = int(qs.get("offset", 0))

    db = get_client()

    count_resp = (
        db.table("events")
        .select("id", count="exact")
        .eq("status", "published")
        .eq("section", "pokemon")
        .eq("event_type", "product_drop")
        .execute()
    )

    data_resp = (
        db.table("events")
        .select(
            "id, slug, title, description, start_at, "
            "brand, tags, image_url, image_url_sm, "
            "image_alt, image_blurhash, image_width, image_height, "
            "og_image_url, social_image_url"
        )
        .eq("status", "published")
        .eq("section", "pokemon")
        .eq("event_type", "product_drop")
        .order("start_at", desc=False)
        .range(offset, offset + limit - 1)
        .execute()
    )

    total = count_resp.count or 0
    items = data_resp.data or []

    return ok(paginated(items, total, limit, offset), origin=origin)


# ── GET /pokemon/retailers ────────────────────────────────────────────────────

def pokemon_retailers(event: dict, ctx) -> dict:
    """Return the full NoVa retailer matrix — static data from the scraper config."""
    origin = event.get("_origin")
    # Import directly from the scraper module (same data, no DB query needed)
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "events-scraper"))

    try:
        from scrapers.pokemon.drops_scraper import get_nova_retailers
        retailers = get_nova_retailers()
    except ImportError:
        # Fallback if scraper not co-deployed — return static summary
        retailers = _static_retailer_summary()

    qs       = event.get("queryStringParameters") or {}
    ret_type = qs.get("type")  # big_box | specialty | online

    if ret_type:
        retailers = [r for r in retailers if r.get("type") == ret_type]

    return ok({
        "retailers": retailers,
        "total":     len(retailers),
    }, origin=origin)


def _static_retailer_summary() -> list[dict]:
    """Minimal static fallback if scraper module not available."""
    return [
        {"name": "Target",              "type": "big_box",   "search_url": "https://www.target.com/s?searchTerm=pokemon+tcg"},
        {"name": "Walmart",             "type": "big_box",   "search_url": "https://www.walmart.com/search?q=pokemon+tcg"},
        {"name": "GameStop",            "type": "big_box",   "search_url": "https://www.gamestop.com/search#q=pokemon+tcg"},
        {"name": "Best Buy",            "type": "big_box",   "search_url": "https://www.bestbuy.com/site/searchpage.jsp?st=pokemon+tcg"},
        {"name": "Costco",              "type": "big_box",   "search_url": "https://www.costco.com/CatalogSearch?keyword=pokemon"},
        {"name": "Sam's Club",          "type": "big_box",   "search_url": "https://www.samsclub.com/s/pokemon"},
        {"name": "Five Below",          "type": "big_box",   "search_url": "https://www.fivebelow.com/content/search?q=pokemon"},
        {"name": "Nerd Rage Gaming",    "type": "specialty", "search_url": "https://www.nerdragegaming.com/"},
        {"name": "Battlegrounds",       "type": "specialty", "search_url": "https://battlegroundsgames.com/pokemon/"},
        {"name": "The Game Parlor",     "type": "specialty", "search_url": "https://thegameparlor.com/"},
        {"name": "Collector's Cache",   "type": "specialty", "search_url": "https://collectorscachegames.com/pokemon/"},
        {"name": "Dream Wizards",       "type": "specialty", "search_url": "https://www.dreamwizards.com/"},
        {"name": "TCGPlayer",           "type": "online",    "search_url": "https://www.tcgplayer.com/search/pokemon/product"},
        {"name": "Pokémon Center",      "type": "online",    "search_url": "https://www.pokemoncenter.com/category/trading-card-game"},
    ]
