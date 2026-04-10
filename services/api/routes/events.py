"""
Events endpoints:
  GET  /events              — paginated list with filters
  GET  /events/featured     — curated featured events
  GET  /events/upcoming     — next 7 days
  GET  /events/{slug}       — single event detail
  POST /events/search       — pgvector semantic search
"""
from __future__ import annotations

import json
import os

from db import get_client
from models import SearchRequest, event_to_response, paginated
from router import ok, error

_EMBED_MODEL = "text-embedding-3-small"
_MAX_LIMIT   = 100


# ── GET /events ────────────────────────────────────────────────────────────────

def list_events(event: dict, ctx) -> dict:
    qs     = event.get("queryStringParameters") or {}
    origin = event.get("_origin")

    limit      = min(int(qs.get("limit", 20)), _MAX_LIMIT)
    offset     = int(qs.get("offset", 0))
    section    = qs.get("section", "main")
    category   = qs.get("category")
    location_id = qs.get("location_id")
    start_date = qs.get("start_date")
    end_date   = qs.get("end_date")
    tags       = qs.get("tags")          # comma-separated
    event_type = qs.get("event_type")
    is_free    = qs.get("is_free")

    db = get_client()

    from datetime import datetime, timezone
    # Default: only show upcoming/current events (start_at >= today)
    # Override by passing start_date explicitly
    now_utc       = datetime.now(timezone.utc)
    default_start = start_date or now_utc.strftime("%Y-%m-%d")
    now_iso       = now_utc.isoformat()

    # Count query (same filters, no pagination)
    count_q = (
        db.table("events")
        .select("id", count="exact")
        .eq("status", "published")
        .eq("section", section)
        .gte("start_at", default_start)
        # Exclude events whose end_at has already passed
        .or_(f"end_at.is.null,end_at.gte.{now_iso}")
    )

    # Data query
    data_q = (
        db.table("events")
        .select(
            "id, slug, title, full_description, short_description, start_at, end_at, "
            "venue_name, address, lat, lng, location_id, "
            "event_type, section, brand, tags, age_min, age_max, "
            "is_free, cost_description, registration_url, "
            "image_url, image_url_md, image_url_sm, image_alt, "
            "image_width, image_height, image_blurhash, "
            "og_image_url, social_image_url, "
            "categories(name, slug)"
        )
        .eq("status", "published")
        .eq("section", section)
        .gte("start_at", default_start)
        # Exclude events whose end_at has already passed
        .or_(f"end_at.is.null,end_at.gte.{now_iso}")
        .order("start_at", desc=False)
        .range(offset, offset + limit - 1)
    )

    # Apply optional filters (start_date already applied above as default_start)
    if event_type:
        # Support comma-separated list e.g. "event,amusement,seasonal"
        type_list = [t.strip() for t in event_type.split(",") if t.strip()]
        if len(type_list) == 1:
            count_q = count_q.eq("event_type", type_list[0])
            data_q  = data_q.eq("event_type", type_list[0])
        elif len(type_list) > 1:
            count_q = count_q.in_("event_type", type_list)
            data_q  = data_q.in_("event_type", type_list)

    if category:
        # Events are tagged but category_id is not yet populated by the scraper.
        # Filter by tags contains [category_slug] which matches the tag vocabulary.
        count_q = count_q.contains("tags", [category])
        data_q  = data_q.contains("tags", [category])

    if location_id:
        count_q = count_q.eq("location_id", location_id)
        data_q  = data_q.eq("location_id", location_id)

    if end_date:
        count_q = count_q.lte("start_at", end_date)
        data_q  = data_q.lte("start_at", end_date)

    if is_free == "true":
        count_q = count_q.eq("is_free", True)
        data_q  = data_q.eq("is_free", True)

    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        if tag_list:
            count_q = count_q.contains("tags", tag_list)
            data_q  = data_q.contains("tags", tag_list)

    count_resp = count_q.execute()
    data_resp  = data_q.execute()

    total = count_resp.count or 0
    items = [event_to_response(r) for r in (data_resp.data or [])]

    return ok(paginated(items, total, limit, offset), origin=origin)


# ── GET /events/featured ──────────────────────────────────────────────────────

def featured_events(event: dict, ctx) -> dict:
    qs      = event.get("queryStringParameters") or {}
    origin  = event.get("_origin")
    section = qs.get("section", "main")
    limit   = min(int(qs.get("limit", 6)), 12)

    db = get_client()
    resp = (
        db.table("events")
        .select(
            "id, slug, title, start_at, venue_name, "
            "event_type, section, tags, is_free, "
            "image_url, image_url_sm, image_alt, image_blurhash, image_width, image_height"
        )
        .eq("status", "published")
        .eq("section", section)
        .eq("is_featured", True)
        .order("start_at", desc=False)
        .limit(limit)
        .execute()
    )

    return ok({"items": resp.data or []}, origin=origin)


# ── GET /events/upcoming ──────────────────────────────────────────────────────

def upcoming_events(event: dict, ctx) -> dict:
    """Events starting in the next 7 days."""
    from datetime import datetime, timedelta, timezone

    qs      = event.get("queryStringParameters") or {}
    origin  = event.get("_origin")
    section = qs.get("section", "main")
    limit   = min(int(qs.get("limit", 10)), 20)

    now      = datetime.now(timezone.utc)
    week_out = now + timedelta(days=7)

    db = get_client()
    resp = (
        db.table("events")
        .select(
            "id, slug, title, start_at, venue_name, "
            "event_type, section, tags, is_free, "
            "image_url, image_url_sm, image_alt, image_blurhash, image_width, image_height"
        )
        .eq("status", "published")
        .eq("section", section)
        .gte("start_at", now.isoformat())
        .lte("start_at", week_out.isoformat())
        .order("start_at", desc=False)
        .limit(limit)
        .execute()
    )

    return ok({"items": resp.data or []}, origin=origin)


# ── GET /events/{slug} ────────────────────────────────────────────────────────

def get_event(event: dict, ctx) -> dict:
    origin = event.get("_origin")
    slug = (event.get("pathParameters") or {}).get("slug", "")
    if not slug:
        return error("Missing slug", 400, origin)

    db = get_client()
    resp = (
        db.table("events")
        .select(
            "*, categories(name, slug), locations(name, slug, lat, lng)"
        )
        .eq("slug", slug)
        .eq("status", "published")
        .single()
        .execute()
    )

    if not resp.data:
        return error("Event not found", 404, origin)

    return ok(event_to_response(resp.data), origin=origin)


# ── POST /events/search ───────────────────────────────────────────────────────

def search_events(event: dict, ctx) -> dict:
    """Semantic search using pgvector cosine similarity."""
    origin = event.get("_origin")
    body = json.loads(event.get("body") or "{}")

    try:
        req = SearchRequest(**body)
    except Exception as exc:
        return error(str(exc), 400, origin)

    # Generate embedding for query
    try:
        embedding = _embed(req.query)
    except Exception as exc:
        return error(f"Embedding failed: {exc}", 500, origin)

    db = get_client()

    # pgvector nearest-neighbor via Supabase RPC function
    resp = db.rpc(
        "search_events",
        {
            "query_embedding": embedding,
            "match_section":   req.section,
            "match_count":     req.limit,
        },
    ).execute()

    items = [event_to_response(r) for r in (resp.data or [])]
    return ok({"items": items, "query": req.query}, origin=origin)


def _embed(text: str) -> list[float]:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.embeddings.create(
        model=_EMBED_MODEL,
        input=text,
    )
    return resp.data[0].embedding
