"""
Publisher — two paths for scraped events:

1. publish_direct()  → upsert directly to Supabase (fast, no image).
   Events appear on the site immediately after the scraper runs.

2. publish()         → send to SQS for image-gen enrichment (background).
   Image-gen picks up messages, generates images, and updates the DB row.
"""
from __future__ import annotations

import hashlib
import html as html_module
import json
import logging
import os
import re
import urllib.request
import urllib.error
from itertools import islice

import boto3
from urllib.parse import urlparse

from .models import RawEvent

logger = logging.getLogger(__name__)

_sqs = None

# Sites that aggregate events from other sources — their URLs are NOT
# the organizer's own website and should not be stored as registration_url.
_AGGREGATOR_DOMAINS = {
    # Calendar aggregators
    "dullesmoms.com", "patch.com", "macaronikid.com",
    "mommypoppins.com", "dc.kidsoutandabout.com", "kidsoutandabout.com",
    "kidfriendlydc.com", "thingstodoindc.com", "bringthekids.com",
    # Local news / blogs
    "restonow.com", "arlnow.com", "ffxnow.com", "loudounnow.com",
    "insidenova.com", "alxnow.com", "tysonsreporter.com",
    "princewilliamtimes.com", "potomaclocal.com", "novatoday.6amcity.com",
    # Parenting sites / magazines
    "theloudounmoms.com", "northernvirginiamag.com", "funinfairfaxva.com",
    "novamomsblog.com", "fairfaxfamilyfun.com",
    # Tourism boards (they aggregate from venues)
    "visitfairfax.org", "visitloudoun.org", "visitalexandriava.com", "visitarlington.com",
    # Deal / coupon aggregators — their article URLs are NOT the brand's deal page
    "hip2save.com", "krazycouponlady.com", "slickdeals.net",
    "dealnews.com", "fatwallet.com", "thekrazy couponlady.com",
    # News aggregators used by Google News RSS deals
    "news.google.com", "googlenewsrss",
}


def _is_aggregator(url: str | None) -> bool:
    """Return True if this URL belongs to a known event aggregator site."""
    if not url:
        return False
    try:
        host = urlparse(url).hostname or ""
        host = host.lower().removeprefix("www.")
        return host in _AGGREGATOR_DOMAINS or any(
            host.endswith("." + d) for d in _AGGREGATOR_DOMAINS
        )
    except Exception:
        return False


def _get_sqs():
    global _sqs
    if _sqs is None:
        _sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
    return _sqs


def _chunks(iterable, size: int):
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def _clean_text(value: str) -> str:
    """Decode HTML entities from scraped text fields (e.g. &#038; → &, &#8217; → ')."""
    if not value:
        return value
    return html_module.unescape(value)


def _normalize_title(title: str) -> str:
    """
    Normalize a title for cross-source deduplication.
    Strips special characters and compresses whitespace so that
    "LEGO Club @ Fairfax Library" and "Lego Club - Fairfax Library"
    compare as equal and collapse to a single event.
    """
    t = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    return re.sub(r"\s+", " ", t).strip()


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
        key = (_normalize_title(e.title), date_key)
        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(e)
    if len(deduped) < len(events):
        logger.info("Deduped %d → %d events (removed %d same-title-date dupes)", len(events), len(deduped), len(events) - len(deduped))
    events = deduped

    for event in events:
        try:
            source_url = event.source_url or event.registration_url or ""

            # Only store a registration_url that points to the organizer's own
            # site, not to an aggregator page (dullesmoms, patch, etc.).
            # Prefer event.registration_url, then fall back to source_url only
            # when neither is an aggregator URL.
            raw_reg = event.registration_url or ""
            if raw_reg and not _is_aggregator(raw_reg):
                registration_url = raw_reg
            elif source_url and not _is_aggregator(source_url):
                registration_url = source_url
            else:
                registration_url = None

            # ── Quality gate: drop "ghost events" ──────────────────────────────
            # When ALL three conditions are true, the event is unactionable:
            #   1. Source is an aggregator domain (can't use their URL as CTA)
            #   2. start_at time is midnight (AI couldn't find the real event time)
            #   3. No registration_url found (users have nowhere to go)
            # These events have wrong/missing times AND no CTA — publishing them
            # damages site credibility (e.g. "Celebrate Reston at 12:00 AM").
            if registration_url is None and _is_aggregator(source_url):
                start_dt = event.start_at
                start_hour = start_dt.hour if hasattr(start_dt, 'hour') else 0
                start_min  = start_dt.minute if hasattr(start_dt, 'minute') else 0
                if start_hour == 0 and start_min == 0:
                    logger.warning(
                        "Dropping ghost event '%s' from %s — aggregator source, "
                        "midnight time, no registration URL",
                        event.title, source_url,
                    )
                    continue

            title_clean = _clean_text(event.title)
            row = {
                "slug":             event.slug or _make_slug(title_clean, event.start_at),
                "title":            title_clean,
                "full_description": _clean_text(event.description),
                "short_description": "",
                "start_at":         event.start_at.isoformat(),
                "end_at":           event.end_at.isoformat() if event.end_at else None,
                "venue_name":       _clean_text(event.venue_name or event.location_name or ""),
                "address":          _clean_text(event.address or event.location_address or ""),
                "location_text":    _clean_text(event.location_text or ""),
                "lat":              event.lat,
                "lng":              event.lng,
                "tags":             event.tags,
                "event_type":       event.event_type.value,
                "section":          event.section,
                "brand":            event.brand or None,
                "is_free":          event.is_free,
                "cost_description": event.cost_description or None,
                "registration_url": registration_url,
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
