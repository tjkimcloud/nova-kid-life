"""
Image sourcing — find the best existing image before falling back to AI generation.

Priority cascade:
  1. Scraped image_url already on the event (most events have one)
  2. Google Places Photos API for known venues / parks
  3. Unsplash API — free stock photo matched to event category/tags
  4. Pexels API  — free stock photo fallback
  5. Return None → caller triggers AI generation (last resort)
"""
from __future__ import annotations

import os
import re
import httpx


# ── Keyword mapping ────────────────────────────────────────────────────────────

# event_type → search terms that produce good, relevant stock photos
_EVENT_TYPE_KEYWORDS: dict[str, str] = {
    "storytime":        "children storytime library books reading",
    "stem":             "children science experiment stem learning",
    "outdoor":          "family outdoor nature hike park",
    "birthday_freebie": "kids birthday celebration fun",
    "deal":             "family restaurant dining kids",
    "amusement":        "amusement park family fun rides",
    "seasonal":         "family seasonal holiday festival",
    "pokemon_tcg":      "pokemon trading card game kids",
    "product_drop":     "pokemon cards booster pack",
    "event":            "family kids activity fun",
}

# category name → search terms
_CATEGORY_KEYWORDS: dict[str, str] = {
    "storytime":    "children storytime library reading",
    "stem":         "children science technology engineering",
    "outdoor":      "family nature outdoor adventure",
    "arts":         "children art craft painting creative",
    "sports":       "kids sports active outdoor play",
    "music":        "children music performance concert",
    "theater":      "children theater performance stage",
    "cooking":      "children cooking baking kitchen",
    "animals":      "kids animals farm petting zoo",
    "history":      "family museum history education",
    "holiday":      "family holiday seasonal celebration",
    "community":    "community family neighborhood event",
    "fitness":      "family fitness active wellness",
    "free":         "family kids activity fun outdoor",
    "pokemon":      "pokemon trading card game",
}

# tag → search terms (partial match, lower-case)
_TAG_KEYWORDS: dict[str, str] = {
    "toddler":   "toddler play learning",
    "baby":      "baby infant play",
    "teen":      "teenager youth activity",
    "free":      "family outdoor park",
    "nature":    "family nature outdoor",
    "library":   "library children reading",
    "museum":    "family museum learning",
    "farm":      "family farm animals harvest",
    "hike":      "family hiking trail nature",
    "art":       "children art craft creative",
    "music":     "children music performance",
    "swim":      "kids swimming pool water",
    "yoga":      "family yoga wellness calm",
    "lego":      "children lego building blocks",
    "coding":    "children coding computer learning",
    "pokemon":   "pokemon card game",
    "science":   "children science experiment",
}


def _build_search_query(event: dict) -> str:
    """Build a stock photo search query from event metadata."""
    # Try event_type first
    event_type = (event.get("event_type") or "").lower()
    if event_type in _EVENT_TYPE_KEYWORDS:
        return _EVENT_TYPE_KEYWORDS[event_type]

    # Try category name
    category = ""
    cat = event.get("categories")
    if isinstance(cat, dict):
        category = (cat.get("name") or cat.get("slug") or "").lower()
    elif isinstance(cat, str):
        category = cat.lower()

    for key, terms in _CATEGORY_KEYWORDS.items():
        if key in category:
            return terms

    # Try tags
    tags = event.get("tags") or []
    for tag in tags:
        tag_lower = tag.lower()
        for key, terms in _TAG_KEYWORDS.items():
            if key in tag_lower:
                return terms

    # Generic fallback
    return "family kids activity fun northern virginia"


# ── Google Places Photos ───────────────────────────────────────────────────────

_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Northern Virginia venue name → known Google Place ID (pre-seeded for speed)
_KNOWN_PLACE_IDS: dict[str, str] = {
    "fairfax county library":       "ChIJV0MiVuLAt4kRHJiPWgbdEMo",
    "george mason university":      "ChIJO0mFKA-_t4kRWOt3C_4Z0Aw",
    "reston town center":           "ChIJH0sRAZK3t4kRVT-6VsY9P3Q",
    "wolf trap":                    "ChIJo8YlXo-_t4kRRBdSifqJEqc",
    "burke lake park":              "ChIJXwdqKlDAt4kRhXlXJMFH8yU",
    "meadowlark botanical gardens": "ChIJZ0JKvYK3t4kRTLm0R6SyLDQ",
    "claude moore colonial farm":   "ChIJtXe8IEi3t4kRsS08Npt5pJQ",
    "sully historic site":          "ChIJKwb7aSvAt4kR2Nq2UGFl-j8",
}


def _normalize(name: str) -> str:
    return re.sub(r"\s+", " ", name.lower().strip())


def _place_id_for_venue(venue_name: str) -> str | None:
    """Return a known Place ID or search Places API for the venue."""
    normalized = _normalize(venue_name)

    for key, place_id in _KNOWN_PLACE_IDS.items():
        if key in normalized or normalized in key:
            return place_id

    if not _PLACES_API_KEY:
        return None

    try:
        resp = httpx.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
            params={
                "input": f"{venue_name} Northern Virginia",
                "inputtype": "textquery",
                "fields": "place_id",
                "key": _PLACES_API_KEY,
            },
            timeout=5,
        )
        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            return candidates[0]["place_id"]
    except Exception:
        pass

    return None


def _fetch_place_photo(place_id: str, max_width: int = 1200) -> str | None:
    """Return the redirect URL of the first photo for a Place ID."""
    if not _PLACES_API_KEY:
        return None

    try:
        resp = httpx.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params={
                "place_id": place_id,
                "fields": "photos",
                "key": _PLACES_API_KEY,
            },
            timeout=5,
        )
        data = resp.json()
        photos = data.get("result", {}).get("photos", [])
        if not photos:
            return None

        photo_ref = photos[0]["photo_reference"]
        return (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth={max_width}&photo_reference={photo_ref}&key={_PLACES_API_KEY}"
        )
    except Exception:
        return None


# ── Unsplash ───────────────────────────────────────────────────────────────────

_UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")


def _fetch_unsplash(query: str) -> str | None:
    """Return a landscape photo URL from Unsplash matching the query. Free tier: 50 req/hr."""
    if not _UNSPLASH_ACCESS_KEY:
        return None

    try:
        resp = httpx.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query":       query,
                "orientation": "landscape",
                "per_page":    1,
                "content_filter": "high",  # safe content only
            },
            headers={"Authorization": f"Client-ID {_UNSPLASH_ACCESS_KEY}"},
            timeout=8,
        )
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return None

        # Use the regular size URL (1080px wide) — good quality, reasonable file size
        urls = results[0].get("urls", {})
        return urls.get("regular") or urls.get("full")
    except Exception:
        return None


# ── Pexels ─────────────────────────────────────────────────────────────────────

_PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")


def _fetch_pexels(query: str) -> str | None:
    """Return a landscape photo URL from Pexels matching the query. Free, unlimited."""
    if not _PEXELS_API_KEY:
        return None

    try:
        resp = httpx.get(
            "https://api.pexels.com/v1/search",
            params={
                "query":       query,
                "orientation": "landscape",
                "per_page":    1,
                "size":        "large",
            },
            headers={"Authorization": _PEXELS_API_KEY},
            timeout=8,
        )
        data = resp.json()
        photos = data.get("photos", [])
        if not photos:
            return None

        # large2x is ~1200px wide, perfect for our hero
        src = photos[0].get("src", {})
        return src.get("large2x") or src.get("large")
    except Exception:
        return None


# ── Public API ─────────────────────────────────────────────────────────────────

def find_source_image(event: dict) -> str | None:
    """
    Return the best available image URL for this event, or None.

    Priority:
      1. Scraped image on event row
      2. Google Places photo for venue
      3. Unsplash free stock photo (keyword-matched)
      4. Pexels free stock photo (keyword-matched)
      5. None → caller triggers AI generation

    Args:
        event: Supabase events row dict (or partial dict from scraper)

    Returns:
        An image URL string, or None if no image could be found.
    """
    # 1. Scraped image
    scraped = event.get("image_url", "")
    if scraped and _looks_like_image(scraped):
        return scraped

    # 2. Google Places
    location_name = event.get("location_name", "") or event.get("venue", "")
    if location_name:
        place_id = _place_id_for_venue(location_name)
        if place_id:
            photo_url = _fetch_place_photo(place_id)
            if photo_url:
                return photo_url

    # 3–4. Free stock photos — skip for social-only types (deals/product drops)
    # that will have better results from AI-generated branded imagery
    event_type = (event.get("event_type") or "").lower()
    if event_type not in ("deal", "product_drop"):
        query = _build_search_query(event)

        photo = _fetch_unsplash(query)
        if photo:
            return photo

        photo = _fetch_pexels(query)
        if photo:
            return photo

    # 5. No image found — caller will generate via AI
    return None


def _looks_like_image(url: str) -> bool:
    """Sanity-check: reject placeholder/icon URLs, allow real images."""
    url_lower = url.lower()

    if not url_lower.startswith("http"):
        return False

    bad_patterns = [
        "placeholder", "default", "no-image", "noimage",
        "icon", "logo", "avatar", "blank", "missing",
        "1x1", "pixel", "spacer",
    ]
    if any(p in url_lower for p in bad_patterns):
        return False

    good_patterns = [
        ".jpg", ".jpeg", ".png", ".webp", ".gif",
        "/images/", "/photos/", "/media/", "/uploads/",
        "cloudinary", "imgix", "twimg", "fbcdn",
        "unsplash", "pexels",
    ]
    return any(p in url_lower for p in good_patterns)
