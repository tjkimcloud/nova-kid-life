"""
events-scraper Lambda handler.
Triggered by: EventBridge schedule (daily 6am EST) or manual invocation.

Event payload:
  { "source": "eventbridge" | "manual", "targets": ["all"] | ["fairfax-library", ...] }
"""
from __future__ import annotations

import importlib
import json
import logging
import os
from pathlib import Path

from scrapers.publisher import publish
from scrapers.tier2.ai_extractor import AITier2Scraper

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load source registry
_SOURCES_PATH = Path(__file__).parent / "config" / "sources.json"
with open(_SOURCES_PATH) as f:
    _SOURCES = json.load(f)

_QUEUE_URL = os.environ.get("EVENTS_QUEUE_URL", "")


def handler(event: dict, context) -> dict:
    logger.info("Scraper invoked: %s", json.dumps(event))

    targets = event.get("targets", ["all"])
    run_all = "all" in targets

    stats = {"scraped": 0, "published": 0, "errors": 0, "sources": {}}

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
            published = publish(events, _QUEUE_URL) if _QUEUE_URL else len(events)
            stats["scraped"] += len(events)
            stats["published"] += published
            stats["sources"][name] = {"scraped": len(events), "published": published}
            logger.info("[%s] scraped=%d published=%d", name, len(events), published)
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
            events = scraper.scrape()
            published = publish(events, _QUEUE_URL) if _QUEUE_URL else len(events)
            stats["scraped"] += len(events)
            stats["published"] += published
            stats["sources"][name] = {"scraped": len(events), "published": published}
            logger.info("[%s] AI scraped=%d published=%d", name, len(events), published)
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
            published = publish(events, _QUEUE_URL) if _QUEUE_URL else len(events)
            stats["scraped"] += len(events)
            stats["published"] += published
            stats["sources"][name] = {"scraped": len(events), "published": published, "section": "pokemon"}
            logger.info("[%s] Pokemon scraped=%d published=%d", name, len(events), published)
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
            published = publish(events, _QUEUE_URL) if _QUEUE_URL else len(events)
            stats["scraped"] += len(events)
            stats["published"] += published
            stats["sources"][name] = {"scraped": len(events), "published": published}
            logger.info("[%s] Deal scraped=%d published=%d", name, len(events), published)
        except Exception as exc:
            logger.exception("[%s] Deal scraper failed: %s", name, exc)
            stats["errors"] += 1
            stats["sources"][name] = {"error": str(exc)}

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
