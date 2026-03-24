"""
events-scraper Lambda handler.
Triggered by: EventBridge schedule (weekly Wednesday 6am EST) or manual invocation.

Event payload:
  { "source": "eventbridge" | "manual", "targets": ["all"] | ["fairfax-library", ...] }
"""
from __future__ import annotations

import importlib
import json
import logging
import os
from pathlib import Path

from scrapers.publisher import publish_direct
from scrapers.source_cache import SourceCache
from scrapers.tier2.ai_extractor import AITier2Scraper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _load_secrets_from_ssm() -> None:
    """Resolve *_PARAM env vars by fetching their values from SSM and
    injecting the plaintext values as the canonical env var names."""
    param_map = {
        "OPENAI_API_KEY_PARAM":       "OPENAI_API_KEY",
        "SUPABASE_URL_PARAM":         "SUPABASE_URL",
        "SUPABASE_KEY_PARAM":         "SUPABASE_SERVICE_KEY",
        "MEETUP_CLIENT_ID_PARAM":     "MEETUP_CLIENT_ID",
        "MEETUP_SECRET_PARAM":        "MEETUP_CLIENT_SECRET",
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
        logger.warning("SSM bootstrap warning: %s", exc)


# Bootstrap secrets once at container init
_load_secrets_from_ssm()

# Load source registry
_SOURCES_PATH = Path(__file__).parent / "config" / "sources.json"
with open(_SOURCES_PATH) as f:
    _SOURCES = json.load(f)

# SQS queue no longer used — scraper upserts directly to Supabase
# _QUEUE_URL kept here in case image enrichment is re-enabled later
_QUEUE_URL = os.environ.get("EVENTS_QUEUE_URL", "")


def handler(event: dict, context) -> dict:
    logger.info("Scraper invoked: %s", json.dumps(event))

    targets = event.get("targets", ["all"])
    run_all = "all" in targets

    stats = {"scraped": 0, "published": 0, "errors": 0, "sources": {}}

    # Load content hash cache once — used by all Tier 2 scrapers to skip
    # unchanged pages and avoid redundant GPT extraction calls
    source_cache = SourceCache()
    source_cache.load()

    def _publish(events, name, extra=None):
        """Upsert directly to Supabase — no image pipeline, events visible immediately."""
        direct = publish_direct(events)
        stats["scraped"]   += len(events)
        stats["published"] += direct
        entry = {"scraped": len(events), "published": direct}
        if extra:
            entry.update(extra)
        stats["sources"][name] = entry
        logger.info("[%s] scraped=%d published=%d", name, len(events), direct)

    # ── Tier 1: Structured scrapers ───────────────────────────────────────────
    for source_config in _SOURCES.get("tier1_events", []):
        if not source_config.get("enabled"):
            continue
        name = source_config["name"]
        if not run_all and name not in targets:
            continue

        try:
            scraper = _load_class(source_config["class"])()
            events = scraper.scrape()
            _publish(events, name)
        except Exception as exc:
            logger.exception("[%s] Scraper failed: %s", name, exc)
            stats["errors"] += 1
            stats["sources"][name] = {"error": str(exc)}

    # ── Tier 2: AI-extracted sources ──────────────────────────────────────────
    for source_config in _SOURCES.get("tier2_events", []):
        if not source_config.get("enabled"):
            continue
        name = source_config["name"]
        if not run_all and name not in targets:
            continue

        try:
            scraper = AITier2Scraper(
                source_name=name,
                url=source_config["url"],
                tags=source_config.get("tags", []),
            )
            scraper._source_cache = source_cache
            events = scraper.scrape()
            _publish(events, name)
        except Exception as exc:
            logger.exception("[%s] AI scraper failed: %s", name, exc)
            stats["errors"] += 1
            stats["sources"][name] = {"error": str(exc)}

    # ── Pokémon TCG section ───────────────────────────────────────────────────
    for source_config in _SOURCES.get("pokemon_events", []):
        if not source_config.get("enabled"):
            continue
        name = source_config["name"]
        if not run_all and name not in targets:
            continue

        try:
            scraper_class = source_config.get("class")
            if scraper_class:
                kwargs = {}
                if "queries" in source_config:
                    kwargs["queries"] = source_config["queries"]
                scraper = _load_class(scraper_class)(**kwargs)
            else:
                logger.warning("[%s] No class configured, skipping", name)
                continue

            events = scraper.scrape()
            _publish(events, name, extra={"section": "pokemon"})
        except Exception as exc:
            logger.exception("[%s] Pokemon scraper failed: %s", name, exc)
            stats["errors"] += 1
            stats["sources"][name] = {"error": str(exc)}

    # ── Tier 3: Deal monitors ─────────────────────────────────────────────────
    for source_config in _SOURCES.get("tier3_deals", []):
        if not source_config.get("enabled"):
            continue
        name = source_config["name"]
        if not run_all and name not in targets:
            continue

        try:
            scraper_class = source_config.get("class")
            if scraper_class:
                kwargs = {}
                if "queries" in source_config:
                    kwargs["queries"] = source_config["queries"]
                scraper = _load_class(scraper_class)(**kwargs)
            else:
                logger.warning("[%s] No class configured, skipping", name)
                continue

            events = scraper.scrape()
            _publish(events, name)
        except Exception as exc:
            logger.exception("[%s] Deal scraper failed: %s", name, exc)
            stats["errors"] += 1
            stats["sources"][name] = {"error": str(exc)}

    # Persist content hashes back to Supabase (one bulk upsert)
    source_cache.save()

    logger.info(
        "Scrape complete: scraped=%d published=%d errors=%d",
        stats["scraped"], stats["published"], stats["errors"],
    )

    return {
        "statusCode": 200,
        "body": json.dumps(stats),
    }


def _load_class(dotted_path: str):
    """Dynamically import a class from a dotted module path."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
