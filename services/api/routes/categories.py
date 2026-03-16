"""
GET /categories — all categories with event counts
"""
from __future__ import annotations

from db import get_client
from router import ok


def list_categories(event: dict, ctx) -> dict:
    db = get_client()

    resp = (
        db.table("categories")
        .select("id, name, slug")
        .order("name")
        .execute()
    )

    categories = resp.data or []

    # Attach live event counts per category
    for cat in categories:
        count_resp = (
            db.table("events")
            .select("id", count="exact")
            .eq("status", "published")
            .eq("category_id", cat["id"])
            .execute()
        )
        cat["event_count"] = count_resp.count or 0

    return ok({"categories": categories})
