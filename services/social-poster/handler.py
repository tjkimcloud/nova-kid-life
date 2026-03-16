"""
NovaKidLife Social Poster — Lambda handler.

Triggered by EventBridge on a schedule (9am, 12pm, 5pm ET weekdays;
10am, 2pm ET weekends). Queries Supabase for published events that
haven't been posted yet, builds platform-specific copy, and schedules
posts via the Ayrshare API.

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

from buffer_client import AyrshareClient, Platform
from copy_builder  import build_copy, image_url_for_platform
from scheduler     import next_optimal_slot
from ssm           import get_ssm_parameter

logger  = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

EASTERN   = ZoneInfo("America/New_York")
PLATFORMS = [Platform.TWITTER, Platform.INSTAGRAM, Platform.FACEBOOK]

# Post events starting within the next N days (don't post stale past events)
POST_HORIZON_DAYS = 14

# Max events to post per Lambda invocation (avoid API rate limits)
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
            "id, slug, title, short_description, "
            "start_at, end_at, venue_name, address, "
            "event_type, section, tags, is_free, cost_description, "
            "image_url, og_image_url, social_image_url, "
            "social_posted_platforms"
        )
        .eq("status", "published")
        .gte("start_at", now.isoformat())
        .lte("start_at", horizon.isoformat())
        .not_.contains("social_posted_platforms", [platform.value])
        .order("start_at", desc=False)
        .limit(MAX_EVENTS_PER_RUN)
        .execute()
    )
    return resp.data or []


def _normalize_event(row: dict) -> dict:
    """Map DB column names to the field names expected by copy_builder."""
    row["location_name"]    = row.pop("venue_name",        "")
    row["location_address"] = row.pop("address",           None)
    row["description"]      = row.pop("short_description", "") or ""
    return row


def _mark_posted(supabase, event_id: str, platform: Platform) -> None:
    """Append platform to social_posted_platforms and set social_posted_at."""
    try:
        current = (
            supabase.table("events")
            .select("social_posted_platforms, social_posted_at")
            .eq("id", event_id)
            .single()
            .execute()
        )
        existing = current.data.get("social_posted_platforms") or []
        if platform.value not in existing:
            existing.append(platform.value)

        update_data: dict = {"social_posted_platforms": existing}
        if not current.data.get("social_posted_at"):
            update_data["social_posted_at"] = datetime.now(tz=EASTERN).isoformat()

        supabase.table("events").update(update_data).eq("id", event_id).execute()
    except Exception as exc:
        logger.error("Failed to mark event %s as posted to %s: %s", event_id, platform.value, exc)


def _process_platform(
    supabase,
    client:   AyrshareClient,
    platform: Platform,
    dry_run:  bool,
) -> dict:
    """Post all pending events for one platform. Returns stats dict."""
    events = _get_unposted_events(supabase, platform)
    posted = skipped = errors = 0

    for raw_event in events:
        event = _normalize_event(dict(raw_event))
        try:
            copy      = build_copy(event, platform)
            image_url = image_url_for_platform(event, platform)
            slot      = next_optimal_slot()

            if dry_run:
                logger.info(
                    "[DRY RUN] Would post to %s at %s: %s",
                    platform.value, slot.isoformat(), copy[:80],
                )
                skipped += 1
                continue

            result = client.create_post(
                platform=platform,
                text=copy,
                media_url=image_url,
                scheduled_at=slot.isoformat(),
            )

            _mark_posted(supabase, event["id"], platform)
            logger.info(
                "Scheduled %s post for '%s' at %s (ID: %s)",
                platform.value, event["title"], slot.isoformat(), result.id,
            )
            posted += 1

        except Exception as exc:
            logger.error(
                "Failed to post event '%s' to %s: %s",
                event.get("title", event.get("id")), platform.value, exc,
            )
            errors += 1

    return {"platform": platform.value, "posted": posted, "skipped": skipped, "errors": errors}


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

    supabase = _get_supabase()
    api_key  = get_ssm_parameter("/novakidlife/ayrshare/api-key")

    with AyrshareClient(api_key) as client:
        results = [
            _process_platform(supabase, client, platform, dry_run)
            for platform in platforms
        ]

    total_posted = sum(r["posted"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    logger.info(
        "Social poster complete | posted=%d | errors=%d | results=%s",
        total_posted, total_errors, results,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "posted":  total_posted,
            "errors":  total_errors,
            "results": results,
        }),
    }
