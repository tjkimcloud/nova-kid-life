"""
Publisher — two paths for scraped events:

1. publish_direct()  → upsert directly to Supabase (fast, no image).
   Events appear on the site immediately after the scraper runs.

2. publish()         → send to SQS for image-gen enrichment (background).
   Image-gen picks up messages, generates images, and updates the DB row.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import urllib.request
import urllib.error
from itertools import islice

import boto3

from .models import RawEvent

logger = logging.getLogger(__name__)

_sqs = None


def _get_sqs():
    global _sqs
    if _sqs is None:
        _sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
    return _sqs


def _chunks(iterable, size: int):
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def _make_slug(title: str, start_at) -> str:
    """Generate a stable URL-safe slug from title + date.
    Using date (not source_url) means the same event from different sources
    collapses to one slug and deduplicates on re-publish."""
    base   = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    date_str = start_at.strftime("%Y%m%d") if hasattr(start_at, "strftime") else str(start_at)[:10].replace("-", "")
    suffix = hashlib.md5(date_str.encode()).hexdigest()[:6]
    return f"{base}-{suffix}" if base else f"event-{suffix}"


def publish_direct(events: list[RawEvent]) -> int:
    """
    Upsert events directly to Supabase — events are visible on the site
    immediately (no SQS, no image pipeline).  Image URLs are left empty;
    image-gen will fill them in later if SQS publishing is also active.

    Returns the number of successfully upserted rows.
    """
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not supabase_url or not supabase_key:
        logger.warning("Supabase credentials missing — skipping direct publish")
        return 0

    headers_bytes = {
        "apikey":        supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type":  "application/json",
        "Prefer":        "resolution=merge-duplicates,return=minimal",
    }

    endpoint = f"{supabase_url.rstrip('/')}/rest/v1/events?on_conflict=source_url"
    upserted = 0

    # Deduplicate within this batch: same title + same date = same event.
    # Prevents the same regional event listed on multiple Patch/local pages
    # from creating duplicate rows (keeps first occurrence found).
    seen_keys: set[tuple] = set()
    deduped: list[RawEvent] = []
    for e in events:
        date_key = e.start_at.strftime("%Y-%m-%d") if hasattr(e.start_at, "strftime") else str(e.start_at)[:10]
        key = (e.title.lower().strip(), date_key)
        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(e)
    if len(deduped) < len(events):
        logger.info("Deduped %d → %d events (removed %d same-title-date dupes)", len(events), len(deduped), len(events) - len(deduped))
    events = deduped

    for event in events:
        try:
            source_url = event.source_url or event.registration_url or ""
            row = {
                "slug":             event.slug or _make_slug(event.title, event.start_at),
                "title":            event.title,
                "full_description": event.description,
                "short_description": "",
                "start_at":         event.start_at.isoformat(),
                "end_at":           event.end_at.isoformat() if event.end_at else None,
                "venue_name":       event.venue_name or event.location_name or "",
                "address":          event.address or event.location_address or "",
                "location_text":    event.location_text or "",
                "lat":              event.lat,
                "lng":              event.lng,
                "tags":             event.tags,
                "event_type":       event.event_type.value,
                "section":          event.section,
                "brand":            event.brand or None,
                "is_free":          event.is_free,
                "cost_description": event.cost_description or None,
                "registration_url": event.registration_url or source_url or None,
                "source_url":       source_url,
                "source_name":      event.source_name or None,
                "status":           "published",
            }
            # Strip None so DB uses column defaults
            row = {k: v for k, v in row.items() if v is not None}

            body = json.dumps(row).encode()
            req  = urllib.request.Request(
                endpoint,
                data=body,
                headers={**headers_bytes, "Content-Length": str(len(body))},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=12):
                upserted += 1

        except urllib.error.HTTPError as exc:
            if exc.code == 409:
                # Slug conflict — same event already inserted from another source.
                # The event IS in the DB; count as success and skip.
                upserted += 1
                continue
            body_snippet = exc.read(300).decode(errors="replace")
            logger.warning(
                "Direct upsert HTTP %s for '%s': %s",
                exc.code, event.title, body_snippet,
            )
        except Exception as exc:
            logger.error("Direct upsert error for '%s': %s", event.title, exc)

    logger.info("publish_direct: %d/%d events upserted to Supabase", upserted, len(events))
    return upserted


def publish(events: list[RawEvent], queue_url: str) -> int:
    """
    Publish events to SQS in batches of 10 (SQS max per send_message_batch).
    Returns the total number of successfully published messages.
    """
    if not events:
        return 0

    sqs = _get_sqs()
    published = 0
    failed = 0

    for batch in _chunks(events, 10):
        entries = [
            {
                "Id": str(i),
                "MessageBody": json.dumps(event.to_dict()),
                # Group by source so related events are processed together
                "MessageGroupId": batch[i].source_name
                if queue_url.endswith(".fifo")
                else None,
            }
            for i, event in enumerate(batch)
        ]
        # Remove None MessageGroupId for standard queues
        entries = [{k: v for k, v in e.items() if v is not None} for e in entries]

        try:
            resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
            batch_ok = len(resp.get("Successful", []))
            batch_fail = len(resp.get("Failed", []))
            published += batch_ok
            failed += batch_fail

            if batch_fail:
                for failure in resp.get("Failed", []):
                    logger.error(
                        "SQS publish failed for entry %s: %s — %s",
                        failure["Id"],
                        failure["Code"],
                        failure["Message"],
                    )
        except Exception as exc:
            logger.exception("SQS batch send error: %s", exc)
            failed += len(batch)

    logger.info("Published %d events to SQS (%d failed)", published, failed)
    return published
