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

def _update_event_images(event_id: str, payload: dict) -> None:
    """PATCH the events row with image URLs and metadata."""
    if not _SUPABASE_URL or not _SUPABASE_KEY:
        logger.warning("Supabase credentials not set — skipping DB update")
        return

    url = f"{_SUPABASE_URL}/rest/v1/events?id=eq.{event_id}"
    headers = {
        "apikey":        _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }
    resp = httpx.patch(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()


# ── Core pipeline ──────────────────────────────────────────────────────────────

def process_event(event: dict) -> dict:
    """
    Run the full image pipeline for one event.

    Returns a result dict with status and any error message.
    """
    event_id   = event.get("id", "")
    event_slug = event.get("slug", event_id)
    title      = event.get("title", "event")

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
