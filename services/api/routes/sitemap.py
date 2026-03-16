"""
GET /sitemap — returns all published event slugs for Next.js static sitemap generation.

Used by apps/web at build time to generate /events/[slug] static params.
Also returns pokemon event slugs for /pokemon/events/[slug].
"""
from __future__ import annotations

from db import get_client
from router import ok


def get_sitemap(event: dict, ctx) -> dict:
    db = get_client()

    # Fetch all published event slugs + section + updated_at
    resp = (
        db.table("events")
        .select("slug, section, updated_at, start_at")
        .eq("status", "published")
        .order("start_at", desc=False)
        .execute()
    )

    rows = resp.data or []

    # Split into sections for the frontend to route correctly
    main_events    = [r for r in rows if r.get("section") == "main"]
    pokemon_events = [r for r in rows if r.get("section") == "pokemon"]

    return ok({
        "main_events":    [{"slug": r["slug"], "updated_at": r["updated_at"]} for r in main_events],
        "pokemon_events": [{"slug": r["slug"], "updated_at": r["updated_at"]} for r in pokemon_events],
        "total":          len(rows),
    })
