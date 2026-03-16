"""
Image sourcing — find the best existing image before falling back to AI generation.

Priority cascade:
  1. Scraped image_url already on the event (most events have one)
  2. Google Places Photos API for known venues / parks
  3. Return None → caller triggers AI generation
"""
from __future__ import annotations

import os
import re
import httpx


# ── Google Places Photos ───────────────────────────────────────────────────────

_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")

# Northern Virginia venue name → known Google Place ID (pre-seeded for speed)
_KNOWN_PLACE_IDS: dict[str, str] = {
    "fairfax county library":    "ChIJV0MiVuLAt4kRHJiPWgbdEMo",
    "george mason university":   "ChIJO0mFKA-_t4kRWOt3C_4Z0Aw",
    "reston town center":        "ChIJH0sRAZK3t4kRVT-6VsY9P3Q",
    "wolf trap":                 "ChIJo8YlXo-_t4kRRBdSifqJEqc",
    "burke lake park":           "ChIJXwdqKlDAt4kRhXlXJMFH8yU",
    "meadowlark botanical gardens": "ChIJZ0JKvYK3t4kRTLm0R6SyLDQ",
    "claude moore colonial farm":   "ChIJtXe8IEi3t4kRsS08Npt5pJQ",
    "sully historic site":          "ChIJKwb7aSvAt4kR2Nq2UGFl-j8",
}


def _normalize(name: str) -> str:
    return re.sub(r"\s+", " ", name.lower().strip())


def _place_id_for_venue(venue_name: str) -> str | None:
    """Return a known Place ID or search Places API for the venue."""
    normalized = _normalize(venue_name)

    # Try exact and partial match against known IDs first (free, instant)
    for key, place_id in _KNOWN_PLACE_IDS.items():
        if key in normalized or normalized in key:
            return place_id

    if not _PLACES_API_KEY:
        return None

    # Places Text Search (1 API call, ~$0.017)
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
        # Get photo reference
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

        # Build the photo URL (redirects to actual image)
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth={max_width}&photo_reference={photo_ref}&key={_PLACES_API_KEY}"
        )
        return photo_url

    except Exception:
        return None


# ── Public API ─────────────────────────────────────────────────────────────────

def find_source_image(event: dict) -> str | None:
    """
    Return the best available image URL for this event, or None.

    Args:
        event: Supabase events row dict (or partial dict from scraper)

    Returns:
        An image URL string, or None if no image could be found.
    """
    # 1. Use scraped image if present and looks like a real image URL
    scraped = event.get("image_url", "")
    if scraped and _looks_like_image(scraped):
        return scraped

    # 2. Try Google Places Photos for known venues
    location_name = event.get("location_name", "") or event.get("venue", "")
    if location_name:
        place_id = _place_id_for_venue(location_name)
        if place_id:
            photo_url = _fetch_place_photo(place_id)
            if photo_url:
                return photo_url

    return None


def _looks_like_image(url: str) -> bool:
    """Sanity-check: reject placeholder/icon URLs, allow real images."""
    url_lower = url.lower()

    # Must start with http
    if not url_lower.startswith("http"):
        return False

    # Reject common placeholder / icon patterns
    bad_patterns = [
        "placeholder", "default", "no-image", "noimage",
        "icon", "logo", "avatar", "blank", "missing",
        "1x1", "pixel", "spacer",
    ]
    if any(p in url_lower for p in bad_patterns):
        return False

    # Accept if URL contains an image extension or a CDN image path
    good_patterns = [
        ".jpg", ".jpeg", ".png", ".webp", ".gif",
        "/images/", "/photos/", "/media/", "/uploads/",
        "cloudinary", "imgix", "twimg", "fbcdn",
    ]
    return any(p in url_lower for p in good_patterns)
