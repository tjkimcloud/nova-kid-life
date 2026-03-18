"""
Blog endpoints:
  GET /blog          — paginated list of blog posts
  GET /blog/{slug}   — single blog post with joined event previews
"""
from __future__ import annotations

from db import get_client
from router import ok, error

_MAX_LIMIT = 50


# ── GET /blog ──────────────────────────────────────────────────────────────────

def list_blog_posts(event: dict, ctx) -> dict:
    qs        = event.get("queryStringParameters") or {}
    limit     = min(int(qs.get("limit", 12)), _MAX_LIMIT)
    offset    = int(qs.get("offset", 0))
    post_type = qs.get("post_type")
    area      = qs.get("area")

    db = get_client()

    count_q = db.table("blog_posts").select("id", count="exact")
    data_q  = (
        db.table("blog_posts")
        .select(
            "id, slug, title, meta_description, post_type, area, "
            "date_range_start, date_range_end, event_count, "
            "hero_image_url, published_at"
        )
        .order("published_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    if post_type:
        count_q = count_q.eq("post_type", post_type)
        data_q  = data_q.eq("post_type", post_type)

    if area:
        count_q = count_q.eq("area", area)
        data_q  = data_q.eq("area", area)

    count_resp = count_q.execute()
    data_resp  = data_q.execute()

    total = count_resp.count or 0
    items = data_resp.data or []

    return ok({
        "items":    items,
        "total":    total,
        "limit":    limit,
        "offset":   offset,
        "has_more": (offset + limit) < total,
    })


# ── GET /blog/{slug} ───────────────────────────────────────────────────────────

def get_blog_post(event: dict, ctx) -> dict:
    slug = (event.get("pathParameters") or {}).get("slug", "")
    if not slug:
        return error("Missing slug", 400)

    db = get_client()

    # Fetch the blog post
    post_resp = (
        db.table("blog_posts")
        .select("*")
        .eq("slug", slug)
        .single()
        .execute()
    )

    if not post_resp.data:
        return error("Blog post not found", 404)

    post = post_resp.data

    # Fetch lightweight event previews for the event_ids in this post
    event_ids = post.get("event_ids") or []
    events    = []
    if event_ids:
        events_resp = (
            db.table("events")
            .select(
                "id, slug, title, start_at, venue_name, location_text, "
                "is_free, cost_description, tags, event_type, "
                "image_url_sm, image_alt, image_blurhash, image_width, image_height"
            )
            .in_("id", event_ids)
            .eq("status", "published")
            .order("start_at", desc=False)
            .execute()
        )
        events = events_resp.data or []

    post["events"] = events
    return ok(post)
