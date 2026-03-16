"""
Platform-specific social post copy builder for NovaKidLife.

Generates optimized copy for Twitter/X, Instagram, and Facebook based on
event type, following the strategy defined in skills/social-strategy.md.
"""
from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from buffer_client import Platform

logger = logging.getLogger(__name__)

EASTERN   = ZoneInfo("America/New_York")
SITE_BASE = "https://novakidlife.com"

# ── Char limits ────────────────────────────────────────────────────────────────
# Twitter: t.co wraps all URLs to 23 chars regardless of actual length
TWITTER_URL_CHARS = 23
TWITTER_MAX       = 280

# ── Hashtag library (from skills/social-strategy.md) ──────────────────────────
HASHTAGS_CORE     = ["#NoVaKids", "#NorthernVirginia", "#FamilyFun"]
HASHTAGS_LOCAL    = {
    "fairfax":       "#FairfaxVA",
    "reston":        "#RestonVA",
    "herndon":       "#HerndonVA",
    "vienna":        "#ViennaVA",
    "loudoun":       "#LoudounCounty",
    "leesburg":      "#LeesburgVA",
    "ashburn":       "#AshburnVA",
    "sterling":      "#SterlingVA",
    "arlington":     "#ArlingtonVA",
    "alexandria":    "#AlexandriaVA",
    "manassas":      "#ManassasVA",
    "woodbridge":    "#WoodbridgeVA",
    "centreville":   "#CentrevilleVA",
    "chantilly":     "#ChantillyVA",
    "springfield":   "#SpringfieldVA",
    "mclean":        "#McLeanVA",
    "falls church":  "#FallsChurchVA",
}
HASHTAGS_EVENTS   = ["#KidsActivities", "#ThingsToDoWithKids", "#WeekendFun"]
HASHTAGS_FREE     = ["#FreeKidsEvents", "#FreeFamily"]
HASHTAGS_POKEMON  = ["#PokemonTCG", "#PokemonCards"]

SEASON_HASHTAGS = {
    (3, 4, 5):     ["#SpringFun"],
    (6, 7, 8):     ["#SummerKids", "#SummerFun"],
    (9, 10, 11):   ["#FallFun", "#FallFestival"],
    (12, 1, 2):    ["#HolidayEvents", "#WinterFun"],
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _fmt_date(iso: str) -> str:
    """Format ISO timestamp → 'Saturday, March 21'."""
    dt = datetime.fromisoformat(iso).astimezone(EASTERN)
    return dt.strftime("%A, %B %-d")


def _fmt_time(iso: str) -> str:
    """Format ISO timestamp → '10:00 AM'."""
    dt = datetime.fromisoformat(iso).astimezone(EASTERN)
    return dt.strftime("%-I:%M %p")


def _fmt_date_short(iso: str) -> str:
    """Format ISO timestamp → 'Sat, Mar 21'."""
    dt = datetime.fromisoformat(iso).astimezone(EASTERN)
    return dt.strftime("%a, %b %-d")


def _event_url(event: dict) -> str:
    section = event.get("section", "main")
    slug    = event["slug"]
    if section == "pokemon":
        return f"{SITE_BASE}/pokemon/events/{slug}"
    return f"{SITE_BASE}/events/{slug}"


def _cost_line(event: dict) -> str:
    if event.get("is_free"):
        return "Free to attend"
    return event.get("cost_description") or "See event page for pricing"


def _city_hashtag(event: dict) -> str | None:
    location = (event.get("location_name") or event.get("venue_name") or "").lower()
    address  = (event.get("location_address") or event.get("address") or "").lower()
    combined = f"{location} {address}"
    for city_key, tag in HASHTAGS_LOCAL.items():
        if city_key in combined:
            return tag
    return None


def _season_hashtags(iso: str) -> list[str]:
    month = datetime.fromisoformat(iso).month
    for months, tags in SEASON_HASHTAGS.items():
        if month in months:
            return tags
    return []


def _tag_hashtags(event: dict, limit: int = 2) -> list[str]:
    """Convert event tags to hashtags (camelCase, max limit)."""
    tags = event.get("tags", [])[:limit]
    return [f"#{''.join(w.capitalize() for w in t.split())}" for t in tags]


def _truncate(text: str, limit: int, suffix: str = "…") -> str:
    if len(text) <= limit:
        return text
    return text[: limit - len(suffix)].rstrip() + suffix


# ── Platform builders ──────────────────────────────────────────────────────────

def _build_twitter(event: dict) -> str:
    """Build Twitter/X copy — max 280 chars, link counts as 23."""
    is_pokemon   = event.get("section") == "pokemon"
    event_type   = event.get("event_type", "event")
    url          = _event_url(event)
    date         = _fmt_date_short(event["start_at"])
    time         = _fmt_time(event["start_at"])
    location     = event.get("location_name") or event.get("venue_name") or ""
    city_tag     = _city_hashtag(event)
    cost         = _cost_line(event)

    # Hashtags (2–3 max for Twitter)
    if is_pokemon:
        tags = HASHTAGS_POKEMON[:2] + (["#NoVaKids"] if city_tag is None else [city_tag])
    elif event_type == "deal":
        tags = ["#NoVaKids", "#FamilyDeals"] + ([city_tag] if city_tag else [])
    else:
        tags = ["#NoVaKids", "#FamilyFun"] + ([city_tag] if city_tag else [])
    hashtag_str = " ".join(tags[:3])

    if is_pokemon:
        emoji = "⚡"
        type_label = {
            "pokemon_tcg":  "Pokémon TCG Event",
            "product_drop": "New Pokémon Set",
        }.get(event_type, "Pokémon Event")
        header = f"{emoji} {type_label}: {event['title']}"
    elif event_type == "deal":
        emoji  = "🚨"
        header = f"{emoji} DEAL: {event['title']}"
    else:
        emoji  = "🎉"
        header = f"{emoji} {event['title']}"

    # Available chars for title (subtract fixed parts + URL placeholder + hashtags)
    details    = f"\n📅 {date} · {time}\n📍 {location}\n{cost}\n{url}\n{hashtag_str}"
    # URL treated as 23 chars by Twitter
    fixed_len  = len(details.replace(url, "x" * TWITTER_URL_CHARS))
    title_budget = TWITTER_MAX - fixed_len - 1  # -1 for newline after header
    safe_header  = _truncate(header, title_budget)

    return f"{safe_header}{details}"


def _build_instagram(event: dict) -> str:
    """Build Instagram caption — full details + heavy hashtag block."""
    is_pokemon = event.get("section") == "pokemon"
    date       = _fmt_date(event["start_at"])
    time       = _fmt_time(event["start_at"])
    location   = event.get("location_name") or event.get("venue_name") or ""
    address    = event.get("location_address") or event.get("address") or ""
    cost       = _cost_line(event)
    short_desc = event.get("description") or event.get("short_description") or ""
    url        = _event_url(event)

    # Shorten description for caption
    desc_snippet = _truncate(short_desc.split("\n")[0], 120)

    # Hashtag block (10–15 tags)
    hashtags = list(dict.fromkeys(  # deduplicate, preserve order
        HASHTAGS_CORE
        + HASHTAGS_EVENTS
        + (HASHTAGS_FREE if event.get("is_free") else [])
        + (HASHTAGS_POKEMON if is_pokemon else [])
        + ([_city_hashtag(event)] if _city_hashtag(event) else [])
        + _season_hashtags(event["start_at"])
        + _tag_hashtags(event, 2)
    ))
    hashtag_block = " ".join(hashtags[:15])

    location_line = location
    if address:
        location_line = f"{location}\n{address}"

    caption = (
        f"{event['title']}\n"
        f".\n"
        f"📅 {date}\n"
        f"⏰ {time}\n"
        f"📍 {location_line}\n"
        f"{'✅ Free to attend' if event.get('is_free') else f'🎟 {cost}'}\n"
        f".\n"
        f"{desc_snippet}\n"
        f".\n"
        f"Link in bio for full details and registration.\n"
        f"👉 {url}\n"
        f".\n.\n.\n"
        f"{hashtag_block}"
    )
    return caption


def _build_facebook(event: dict) -> str:
    """Build Facebook post — medium length, 1–2 hashtags, full logistics."""
    is_pokemon = event.get("section") == "pokemon"
    event_type = event.get("event_type", "event")
    date       = _fmt_date(event["start_at"])
    time       = _fmt_time(event["start_at"])
    location   = event.get("location_name") or event.get("venue_name") or ""
    address    = event.get("location_address") or event.get("address") or ""
    cost       = _cost_line(event)
    short_desc = event.get("description") or event.get("short_description") or ""
    url        = _event_url(event)

    desc_snippet = _truncate(short_desc.split("\n")[0], 200)

    if is_pokemon:
        emoji = "⚡"
    elif event_type == "deal":
        emoji = "🚨"
    elif event.get("is_free"):
        emoji = "🆓"
    else:
        emoji = "🎉"

    city_tag = _city_hashtag(event)
    hashtags = f"#NoVaKids {city_tag}" if city_tag else "#NoVaKids #NorthernVirginia"

    address_line = f"\n📍 {address}, {location}" if address else f"\n📍 {location}"

    post = (
        f"{emoji} {event['title']}\n\n"
        f"📅 {date}\n"
        f"⏰ {time}"
        f"{address_line}\n"
        f"{'✅ Free to attend' if event.get('is_free') else f'🎟 {cost}'}\n\n"
        f"{desc_snippet}\n\n"
        f"Full details → {url}\n\n"
        f"{hashtags}"
    )
    return post


# ── Public interface ───────────────────────────────────────────────────────────

def build_copy(event: dict, platform: Platform) -> str:
    """Build platform-specific post copy for an event.

    Args:
        event:    Event dict (as returned by event_to_response()).
        platform: Target platform.

    Returns:
        Formatted post copy string ready to send to Buffer.
    """
    builders = {
        Platform.TWITTER:   _build_twitter,
        Platform.INSTAGRAM: _build_instagram,
        Platform.FACEBOOK:  _build_facebook,
    }
    builder = builders.get(platform)
    if not builder:
        raise ValueError(f"Unsupported platform: {platform}")

    copy = builder(event)
    logger.debug(
        "Built %s copy for event '%s' (%d chars)",
        platform.value, event.get("title", "?"), len(copy)
    )
    return copy


def image_url_for_platform(event: dict, platform: Platform) -> str | None:
    """Return the best image URL for the given platform.

    - Instagram: 1080×1080 social image (square)
    - Twitter/Facebook: 1200×630 OG image (landscape)
    """
    if platform == Platform.INSTAGRAM:
        return event.get("social_image_url") or event.get("image_url")
    return event.get("og_image_url") or event.get("image_url")
