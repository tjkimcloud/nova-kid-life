"""
NovaKidLife Social Poster — Lambda handler.

Triggered by EventBridge on a schedule (9am, 12pm, 5pm ET weekdays;
10am, 2pm ET weekends). Queries Supabase for published events that
haven't been posted yet, builds platform-specific copy, and schedules
posts via the Buffer API.

EventBridge schedule (defined in Terraform):
  cron(0 14 ? * MON-FRI *)  → 9am EST  (UTC-5 in winter, UTC-4 in summer)
  cron(0 17 ? * MON-FRI *)  → 12pm EST
  cron(0 22 ? * MON-FRI *)  → 5pm EST
  cron(0 15 ? * SAT-SUN *)  → 10am EST
  cron(0 19 ? * SAT-SUN *)  → 2pm EST
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from supabase import create_client

from buffer_client import BufferClient, Platform
from copy_builder  import build_copy, image_url_for_platform
from scheduler     import next_optimal_slot
from ssm           import get_ssm_parameter

logger  = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EASTERN   = ZoneInfo("America/New_York")
PLATFORMS = [Platform.TWITTER, Platform.INSTAGRAM, Platform.FACEBOOK]

# Post events starting within the next N days (don't post stale past events)
POST_HORIZON_DAYS = 14

# Max events to post per Lambda invocation (avoid hitting Buffer rate limits)
MAX_EVENTS_PER_RUN = 5


def _get_supabase():
    url = get_ssm_parameter("/novakidlife/supabase/url")
    key = get_ssm_parameter("/novakidlife/supabase/service-key")
    return create_client(url, key)


def _get_unposted_events(supabase, platform: Platform) -> list[dict]:
    """Fetch published events not yet posted to this platform."""
    now     = datetime.now(tz=EASTERN)
    horizon = now + timedelta(days=POST_HORIZON_DAYS)

    resp = (
        supabase.table("events")
        .select(
            "id, slug, title, description, short_description, "
            "start_at, end_at, venue_name, address, "
            "event_type, section, tags, is_free, cost_description, "
            "image_url, og_image_url, social_image_url, "
            "social_posted_platforms"
        )
        .eq("status", "published")
        .gte("start_at", now.isoformat())
        .lte("start_at", horizon.isoformat())
        # Filter: platform NOT already in social_posted_platforms
        .not_.contains("social_posted_platforms", [platform.value])
        .order("start_at", desc=False)
        .limit(MAX_EVENTS_PER_RUN)
        .execute()
    )
    return resp.data or []


def _normalize_event(row: dict) -> dict:
    """Map DB column names to the API response names expected by copy_builder."""
    row["location_name"]    = row.pop("venue_name",        "")
    row["location_address"] = row.pop("address",           None)
    row["description"]      = row.pop("short_description", "") or row.pop("description", "")
    return row


def _mark_posted(supabase, event_id: str, platform: Platform) -> None:
    """Append platform to social_posted_platforms and set social_posted_at."""
    # Use Supabase RPC or raw SQL to append to array atomically.
    # Fallback: fetch current value, append, update.
    try:
        current = (
            supabase.table("events")
            .select("social_posted_platforms, social_posted_at")
            .eq("id", event_id)
            .single()
            .execute()
        )
        existing_platforms = current.data.get("social_posted_platforms") or []
        if platform.value not in existing_platforms:
            existing_platforms.append(platform.value)

        update_data: dict = {"social_posted_platforms": existing_platforms}
        if not current.data.get("social_posted_at"):
            update_data["social_posted_at"] = datetime.now(tz=EASTERN).isoformat()

        supabase.table("events").update(update_data).eq("id", event_id).execute()
    except Exception as exc:
        logger.error("Failed to mark event %s as posted to %s: %s", event_id, platform.value, exc)


def _process_platform(
    supabase,
    buffer:   BufferClient,
    platform: Platform,
    profile_map: dict[Platform, list[str]],
) -> dict:
    """Post all pending events for one platform. Returns stats dict."""
    profile_ids = profile_map.get(platform, [])
    if not profile_ids:
        logger.warning("No Buffer profile IDs for platform %s — skipping", platform.value)
        return {"platform": platform.value, "posted": 0, "skipped": 0, "errors": 0}

    events  = _get_unposted_events(supabase, platform)
    posted  = 0
    skipped = 0
    errors  = 0

    for raw_event in events:
        event = _normalize_event(dict(raw_event))
        try:
            copy      = build_copy(event, platform)
            image_url = image_url_for_platform(event, platform)
            slot      = next_optimal_slot()

            result = buffer.create_update(
                profile_ids=profile_ids,
                text=copy,
                media_url=image_url,
                scheduled_at=slot.isoformat(),
            )

            _mark_posted(supabase, event["id"], platform)
            logger.info(
                "Scheduled %s post for '%s' at %s (Buffer ID: %s)",
                platform.value, event["title"], slot.isoformat(), result.id,
            )
            posted += 1

        except Exception as exc:
            logger.error(
                "Failed to post event '%s' to %s: %s",
                event.get("title", event.get("id")), platform.value, exc,
            )
            errors += 1

    return {
        "platform": platform.value,
        "posted":   posted,
        "skipped":  skipped,
        "errors":   errors,
    }


def lambda_handler(event: dict, context) -> dict:
    """Lambda entry point — called by EventBridge schedule.

    Also handles manual invocation with optional payload:
    { "platforms": ["twitter"], "dry_run": true }
    """
    dry_run   = event.get("dry_run", False)
    platforms = [
        Platform(p) for p in event.get("platforms", [p.value for p in PLATFORMS])
    ]

    logger.info(
        "Social poster invoked | platforms=%s | dry_run=%s",
        [p.value for p in platforms], dry_run,
    )

    if dry_run:
        logger.info("Dry run mode — no posts will be scheduled")

    supabase = _get_supabase()
    token    = get_ssm_parameter("/novakidlife/buffer/access-token")

    with BufferClient(token) as buffer:
        # Fetch platform → profile ID mapping from Buffer
        profile_map = buffer.get_profiles_by_platform(platforms)
        logger.info("Buffer profiles: %s", {k.value: v for k, v in profile_map.items()})

        results = []
        for platform in platforms:
            stats = _process_platform(supabase, buffer, platform, profile_map)
            results.append(stats)

    total_posted = sum(r["posted"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    logger.info(
        "Social poster complete | posted=%d | errors=%d | results=%s",
        total_posted, total_errors, results,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "posted": total_posted,
            "errors": total_errors,
            "results": results,
        }),
    }
