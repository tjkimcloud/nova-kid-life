"""
Lambda handler — image generation pipeline.

Triggered by SQS messages from the events scraper.
Each message contains an event row (or partial dict with at minimum: id, slug, title).

Pipeline per event:
  1. Check if images already exist → skip if yes
  2. source   — find existing image (scraped URL or Google Places)
  3. generate — AI image if no source found (website + social separately)
  4. enhance  — warm color grade on all sourced/generated images
  5. process  — resize to all variants, WebP conversion, LQIP + blurhash
  6. alt_text — AI-generated SEO alt text
  7. upload   — S3 with cache headers
  8. db       — update events row with all URLs + metadata
"""
from __future__ import annotations

import json
import logging
import os
import sys


def _load_secrets_from_ssm() -> None:
    """Resolve *_PARAM env vars from SSM into their canonical env var names."""
    param_map = {
        "SUPABASE_URL_PARAM":           "SUPABASE_URL",
        "SUPABASE_KEY_PARAM":           "SUPABASE_SERVICE_KEY",
        "OPENAI_API_KEY_PARAM":         "OPENAI_API_KEY",
        "GOOGLE_PROJECT_ID_PARAM":      "GOOGLE_PROJECT_ID",
        "GOOGLE_LOCATION_PARAM":        "GOOGLE_LOCATION",
        "GOOGLE_SA_JSON_PARAM":         "GOOGLE_SERVICE_ACCOUNT_JSON",
        "GOOGLE_PLACES_API_KEY_PARAM":  "GOOGLE_PLACES_API_KEY",
        "UNSPLASH_ACCESS_KEY_PARAM":    "UNSPLASH_ACCESS_KEY",
        "PEXELS_API_KEY_PARAM":         "PEXELS_API_KEY",
    }
    ssm_paths = {v: os.environ[k] for k, v in param_map.items() if k in os.environ}
    if not ssm_paths:
        return
    try:
        import boto3
        ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        for env_key, param_path in ssm_paths.items():
            if not os.environ.get(env_key):
                result = ssm.get_parameter(Name=param_path, WithDecryption=True)
                os.environ[env_key] = result["Parameter"]["Value"]
    except Exception as exc:
        logging.getLogger(__name__).warning("SSM bootstrap warning: %s", exc)


_load_secrets_from_ssm()

import httpx

# Add service root to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from alt_text  import generate_alt_text
from enhancer  import apply_warm_grade
from generator import generate_image
from processor import process_website_image, process_social_image
from prompts   import get_website_prompt, get_social_prompt, get_pokemon_prompt
from sourcer   import find_source_image
from uploader  import upload_all, image_already_exists

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Supabase REST endpoint for direct DB updates
_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


# ── DB helpers ─────────────────────────────────────────────────────────────────

def _headers() -> dict:
    return {
        "apikey":        _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type":  "application/json",
    }


def _make_slug(title: str, source_url: str) -> str:
    """Generate a URL-safe slug from title + a short hash of source_url."""
    import re
    import hashlib
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    suffix = hashlib.md5(source_url.encode()).hexdigest()[:6]
    return f"{base}-{suffix}" if base else f"event-{suffix}"


def _upsert_event(event: dict) -> dict:
    """Upsert an event row and return the saved row (with slug + id from DB).

    Conflict key: source_url (unique). slug is generated from title + url hash
    so it is always present on INSERT and ignored on UPDATE (merge-duplicates).
    """
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        logger.warning("Supabase credentials not set — skipping upsert")
        return event

    source_url = event.get("source_url", event.get("registration_url", ""))
    title      = event.get("title", "untitled")

    # Map RawEvent fields → DB column names
    row = {
        "slug":             event.get("slug") or _make_slug(title, source_url),
        "title":            title,
        "short_description": event.get("short_description", ""),
        "full_description": event.get("description", event.get("full_description", "")),
        "start_at":         event.get("start_at") or "2026-01-01T00:00:00+00:00",
        "end_at":           event.get("end_at"),
        "venue_name":       event.get("venue_name", event.get("location_name", "")),
        "address":          event.get("address", event.get("location_address", "")),
        "location_text":    event.get("location_text", ""),
        "lat":              event.get("lat"),
        "lng":              event.get("lng"),
        "tags":             event.get("tags", []),
        "event_type":       event.get("event_type", "event"),
        "section":          event.get("section", "main"),
        "brand":            event.get("brand"),
        "is_free":          event.get("is_free", False),
        "cost_description": event.get("cost_description"),
        "registration_url": event.get("registration_url") or source_url,
        "source_url":       source_url,
        "status":           "published",
    }
    # Remove None values to let DB use defaults
    row = {k: v for k, v in row.items() if v is not None}

    url = f"{_SUPABASE_URL}/rest/v1/events?on_conflict=source_url"
    headers = {**_headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
    resp = httpx.post(url, json=row, headers=headers, timeout=15)
    resp.raise_for_status()

    saved = resp.json()
    if isinstance(saved, list) and saved:
        return saved[0]
    return event


def _update_event_images(event_id: str, payload: dict) -> None:
    """PATCH the events row with image URLs and metadata."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        logger.warning("Supabase credentials not set — skipping DB update")
        return

    url = f"{_SUPABASE_URL}/rest/v1/events?id=eq.{event_id}"
    headers = {**_headers(), "Prefer": "return=minimal"}
    resp = httpx.patch(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()


# ── Core pipeline ──────────────────────────────────────────────────────────────

def process_event(event: dict) -> dict:
    """
    Run the full image pipeline for one event.

    Returns a result dict with status and any error message.
    """
    title = event.get("title", "event")

    # Step 0: Upsert event into DB to get the assigned slug/id
    event = _upsert_event(event)

    event_id   = event.get("id", "")
    event_slug = event.get("slug", event_id)

    logger.info("Processing images for event: %s (%s)", title, event_slug)

    # Skip if images already generated (idempotent)
    if image_already_exists(event_slug):
        logger.info("Images already exist for %s — skipping", event_slug)
        return {"status": "skipped", "slug": event_slug}

    try:
        # ── Step 1: Source or generate website image ───────────────────────────
        source_url = find_source_image(event)

        # Route to Pokémon-specific prompts if this is a pokemon section event
        is_pokemon = event.get("section") == "pokemon"

        if source_url:
            logger.info("Using sourced image: %s", source_url)
            raw_bytes = _download_image(source_url)
        else:
            logger.info("No source found — generating with AI")
            website_prompt = (
                get_pokemon_prompt(event, style="website")
                if is_pokemon else get_website_prompt(event)
            )
            raw_bytes = generate_image(website_prompt, size="website")

        # ── Step 2: Warm grade ─────────────────────────────────────────────────
        graded_bytes = apply_warm_grade(raw_bytes)

        # ── Step 3: Process all website variants ──────────────────────────────
        processed = process_website_image(graded_bytes)

        # ── Step 4: Generate social illustration (always AI) ──────────────────
        social_prompt = (
            get_pokemon_prompt(event, style="social")
            if is_pokemon else get_social_prompt(event)
        )
        social_raw = generate_image(social_prompt, size="social")
        social_webp   = process_social_image(social_raw)

        # ── Step 5: Alt text ───────────────────────────────────────────────────
        alt_text = generate_alt_text(event)

        # ── Step 6: Upload to S3 ───────────────────────────────────────────────
        urls = upload_all(
            event_slug = event_slug,
            hero    = processed.hero,
            hero_md = processed.hero_md,
            hero_sm = processed.hero_sm,
            card    = processed.card,
            og      = processed.og,
            social  = social_webp,
        )

        # ── Step 7: Update Supabase ────────────────────────────────────────────
        db_payload = {
            "image_url":       urls.hero,
            "image_url_md":    urls.hero_md,
            "image_url_sm":    urls.hero_sm,
            "og_image_url":    urls.og,
            "social_image_url": urls.social,
            "image_alt":       alt_text,
            "image_width":     1200,
            "image_height":    675,
            "image_blurhash":  processed.blurhash,
            # LQIP stored inline in DB — no CDN round-trip needed
            "image_lqip":      processed.lqip_data_url,
        }
        _update_event_images(event_id, db_payload)

        logger.info("✓ Images complete for %s", event_slug)
        return {"status": "ok", "slug": event_slug, "hero_url": urls.hero}

    except Exception as exc:
        logger.error("Failed to process images for %s: %s", event_slug, exc, exc_info=True)
        return {"status": "error", "slug": event_slug, "error": str(exc)}


def _download_image(url: str) -> bytes:
    """Download image bytes from a URL."""
    resp = httpx.get(url, timeout=20, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


# ── Lambda entry point ─────────────────────────────────────────────────────────

def lambda_handler(event: dict, context) -> dict:
    """
    SQS trigger handler.

    Each SQS record body is a JSON-encoded event dict.
    """
    records = event.get("Records", [])
    logger.info("Received %d SQS records", len(records))

    results = []
    for record in records:
        try:
            event_data = json.loads(record["body"])
        except (json.JSONDecodeError, KeyError) as exc:
            logger.error("Failed to parse SQS record: %s", exc)
            results.append({"status": "parse_error", "error": str(exc)})
            continue

        result = process_event(event_data)
        results.append(result)

    ok_count    = sum(1 for r in results if r.get("status") == "ok")
    skip_count  = sum(1 for r in results if r.get("status") == "skipped")
    error_count = sum(1 for r in results if r.get("status") == "error")

    logger.info(
        "Done — ok: %d  skipped: %d  errors: %d",
        ok_count, skip_count, error_count,
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "processed": len(records),
            "ok":        ok_count,
            "skipped":   skip_count,
            "errors":    error_count,
            "results":   results,
        }),
    }

# Alias for Terraform handler config (handler.handler)
handler = lambda_handler
