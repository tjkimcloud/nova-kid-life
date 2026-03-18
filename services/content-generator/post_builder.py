"""
Core post-building logic for content-generator Lambda.
Queries events, groups them into post specs, generates content via GPT-4o-mini,
and saves to the blog_posts Supabase table.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from openai import OpenAI
from supabase import Client

from prompts import (
    build_weekend_prompt,
    build_location_prompt,
    build_free_events_prompt,
    build_week_ahead_prompt,
    build_indoor_prompt,
)

logger = logging.getLogger(__name__)

_GPT_MODEL      = "gpt-4o-mini"
_MIN_EVENTS     = 3   # don't generate a post with fewer events than this
_MAX_EVENTS     = 40  # cap events sent to GPT to avoid token overflow


# ── Area definitions ───────────────────────────────────────────────────────────

# Maps area keys → (label, county label, location name patterns for DB lookup)
AREAS = {
    "nova":          ("Northern Virginia", "NoVa",            None),   # all sections
    "fairfax":       ("Fairfax County",    "Fairfax County",  ["Fairfax", "Reston", "Herndon", "Vienna", "Springfield", "Burke", "Centreville", "Chantilly", "McLean"]),
    "loudoun":       ("Loudoun County",    "Loudoun County",  ["Ashburn", "Leesburg", "Sterling"]),
    "arlington":     ("Arlington",         "Arlington County",["Arlington"]),
    "alexandria":    ("Alexandria",        "City of Alexandria", ["Alexandria"]),
    "prince_william":("Prince William County", "Prince William", ["Manassas", "Woodbridge"]),
}


@dataclass
class PostSpec:
    post_type:        str
    area:             str
    date_range_start: date
    date_range_end:   date
    area_label:       str
    county_label:     str
    location_names:   Optional[list[str]]


# ── Date helpers ───────────────────────────────────────────────────────────────

def get_upcoming_weekend(ref: date) -> tuple[date, date]:
    """Return (Friday, Sunday) of the next upcoming weekend."""
    days_until_friday = (4 - ref.weekday()) % 7
    if days_until_friday == 0:
        days_until_friday = 7
    friday = ref + timedelta(days=days_until_friday)
    return friday, friday + timedelta(days=2)


def get_upcoming_week(ref: date) -> tuple[date, date]:
    """Return (Monday, Sunday) of the upcoming week."""
    days_until_monday = (7 - ref.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    monday = ref + timedelta(days=days_until_monday)
    return monday, monday + timedelta(days=6)


# ── Supabase helpers ───────────────────────────────────────────────────────────

def _get_location_ids(db: Client, location_names: list[str]) -> list[str]:
    """Resolve location names to Supabase location UUIDs."""
    resp = (
        db.table("locations")
        .select("id, name")
        .in_("name", location_names)
        .execute()
    )
    return [r["id"] for r in (resp.data or [])]


def fetch_events(
    db: Client,
    start: date,
    end: date,
    location_ids: Optional[list[str]] = None,
    free_only: bool = False,
    indoor_only: bool = False,
) -> list[dict]:
    """Fetch published main-section events for a date range."""
    q = (
        db.table("events")
        .select(
            "id, slug, title, short_description, start_at, end_at, "
            "venue_name, location_text, tags, event_type, "
            "is_free, cost_description, registration_url, location_id"
        )
        .eq("status", "published")
        .eq("section", "main")
        .gte("start_at", start.isoformat())
        .lte("start_at", (end + timedelta(days=1)).isoformat())
        .order("is_free", desc=True)   # free events first
        .order("start_at", desc=False)
        .limit(_MAX_EVENTS)
    )

    if location_ids:
        q = q.in_("location_id", location_ids)

    if free_only:
        q = q.eq("is_free", True)

    if indoor_only:
        q = q.contains("tags", ["indoor"])

    resp = q.execute()
    return resp.data or []


def post_exists(db: Client, post_type: str, area: str, start: date) -> bool:
    """Idempotency check — skip if this post was already generated."""
    resp = (
        db.table("blog_posts")
        .select("id")
        .eq("post_type", post_type)
        .eq("area", area)
        .eq("date_range_start", start.isoformat())
        .execute()
    )
    return bool(resp.data)


def save_post(
    db: Client,
    spec: PostSpec,
    title: str,
    content: str,
    meta_description: str,
    event_ids: list[str],
) -> dict:
    slug = _make_slug(spec)
    row = {
        "slug":             slug,
        "title":            title,
        "meta_description": meta_description[:160],
        "content":          content,
        "post_type":        spec.post_type,
        "area":             spec.area,
        "date_range_start": spec.date_range_start.isoformat(),
        "date_range_end":   spec.date_range_end.isoformat(),
        "event_ids":        event_ids,
        "event_count":      len(event_ids),
    }
    resp = db.table("blog_posts").upsert(row, on_conflict="post_type,area,date_range_start").execute()
    return resp.data[0] if resp.data else {}


# ── GPT generation ─────────────────────────────────────────────────────────────

def generate_post_content(openai_client: OpenAI, prompt: str) -> dict:
    """Call GPT-4o-mini and parse the JSON response."""
    resp = openai_client.chat.completions.create(
        model=_GPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a content writer for NovaKidLife, a family events site for Northern Virginia parents. "
                    "You write warm, local, parent-to-parent content. "
                    "Always respond with valid JSON only — no markdown code fences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    raw = resp.choices[0].message.content or "{}"
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.error("GPT returned invalid JSON: %s\nRaw: %s", exc, raw[:500])
        raise


# ── Main orchestrator ──────────────────────────────────────────────────────────

def build_posts_for_trigger(db: Client, openai_client: OpenAI, trigger: str) -> list[dict]:
    """
    Generate all blog posts for a given trigger type.

    trigger: "weekend" | "week_ahead"
    Returns list of saved post records.
    """
    from datetime import date as today_date
    ref = today_date.today()

    if trigger == "weekend":
        start, end = get_upcoming_weekend(ref)
    else:
        start, end = get_upcoming_week(ref)

    specs = _build_specs(trigger, start, end)
    saved = []

    for spec in specs:
        if post_exists(db, spec.post_type, spec.area, spec.date_range_start):
            logger.info("Skipping existing post: %s/%s/%s", spec.post_type, spec.area, spec.date_range_start)
            continue

        # Resolve location IDs for area filtering
        location_ids = None
        if spec.location_names:
            location_ids = _get_location_ids(db, spec.location_names)
            if not location_ids:
                logger.warning("No location IDs found for area %s — skipping", spec.area)
                continue

        # Fetch events
        free_only   = spec.post_type == "free_events"
        indoor_only = spec.post_type == "indoor"
        events = fetch_events(db, start, end, location_ids, free_only, indoor_only)

        if len(events) < _MIN_EVENTS:
            logger.info("Not enough events (%d) for %s/%s — skipping", len(events), spec.post_type, spec.area)
            continue

        # Build prompt
        prompt = _select_prompt(spec, events, start, end)

        # Generate
        try:
            result = generate_post_content(openai_client, prompt)
        except Exception as exc:
            logger.error("GPT generation failed for %s/%s: %s", spec.post_type, spec.area, exc)
            continue

        title            = result.get("title", spec.area_label)
        meta_description = result.get("meta_description", "")
        content          = result.get("content", "")

        if not content:
            logger.warning("Empty content returned for %s/%s", spec.post_type, spec.area)
            continue

        event_ids = [str(e["id"]) for e in events if e.get("id")]
        post = save_post(db, spec, title, content, meta_description, event_ids)
        logger.info("Saved post: %s (slug: %s)", title, post.get("slug"))
        saved.append(post)

    return saved


# ── Spec builder ───────────────────────────────────────────────────────────────

def _build_specs(trigger: str, start: date, end: date) -> list[PostSpec]:
    """Build the list of post specs to generate for a trigger."""
    specs = []

    if trigger == "weekend":
        # 1. Main NoVa weekend roundup
        specs.append(PostSpec("weekend_roundup", "nova", start, end, "Northern Virginia", "NoVa", None))

        # 2. Location-specific roundups for major areas
        for area_key in ["fairfax", "loudoun", "arlington", "alexandria"]:
            label, county, names = AREAS[area_key]
            specs.append(PostSpec("location_specific", area_key, start, end, label, county, names))

        # 3. Free events roundup (NoVa-wide)
        specs.append(PostSpec("free_events", "nova", start, end, "Northern Virginia", "NoVa", None))

        # 4. Indoor roundup (useful Oct–Mar and rainy weekends)
        specs.append(PostSpec("indoor", "nova", start, end, "Northern Virginia", "NoVa", None))

    elif trigger == "week_ahead":
        specs.append(PostSpec("week_ahead", "nova", start, end, "Northern Virginia", "NoVa", None))

    return specs


def _select_prompt(spec: PostSpec, events: list[dict], start: date, end: date) -> str:
    """Select and build the right prompt for a post spec."""
    if spec.post_type == "weekend_roundup":
        return build_weekend_prompt(events, start, end, spec.area_label)
    elif spec.post_type == "location_specific":
        return build_location_prompt(events, start, end, spec.area_label, spec.county_label)
    elif spec.post_type == "free_events":
        return build_free_events_prompt(events, start, end, spec.area_label)
    elif spec.post_type == "week_ahead":
        return build_week_ahead_prompt(events, start, end, spec.area_label)
    elif spec.post_type == "indoor":
        return build_indoor_prompt(events, start, end, spec.area_label)
    else:
        raise ValueError(f"Unknown post_type: {spec.post_type}")


def _make_slug(spec: PostSpec) -> str:
    """Generate a URL slug for a post."""
    area  = spec.area_label.lower().replace(" ", "-").replace(",", "")
    start = spec.date_range_start
    date_str = f"{start.strftime('%B')}-{start.day}".lower()
    end_str  = f"{spec.date_range_end.day}-{spec.date_range_end.year}"

    slugs = {
        "weekend_roundup":   f"things-to-do-this-weekend-{area}-{date_str}-{end_str}",
        "week_ahead":        f"family-events-{area}-week-of-{date_str}-{end_str}",
        "location_specific": f"things-to-do-{area}-this-weekend-{date_str}-{end_str}",
        "free_events":       f"free-things-to-do-with-kids-{area}-{date_str}-{end_str}",
        "indoor":            f"indoor-activities-kids-{area}-{date_str}-{end_str}",
        "date_specific":     f"things-to-do-{area}-{date_str}-{start.year}",
    }

    raw = slugs.get(spec.post_type, f"blog-{spec.post_type}-{area}-{date_str}")
    return re.sub(r"-+", "-", raw).strip("-")
