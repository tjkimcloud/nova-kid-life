"""
GET /locations — all NoVa locations with event counts
"""
from __future__ import annotations

from db import get_client
from router import ok


def list_locations(event: dict, ctx) -> dict:
    db = get_client()

    resp = (
        db.table("locations")
        .select("id, name, slug, lat, lng")
        .order("name")
        .execute()
    )

    locations = resp.data or []

    # Attach live event counts per location
    for loc in locations:
        count_resp = (
            db.table("events")
            .select("id", count="exact")
            .eq("status", "published")
            .eq("location_id", loc["id"])
            .execute()
        )
        loc["event_count"] = count_resp.count or 0

    return ok({"locations": locations})
