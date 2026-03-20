"""
Content hash cache for Tier 2 scraper sources.

Persists per-source cleaned-HTML hashes to Supabase so the scraper skips
GPT extraction entirely when a page hasn't changed since the last run.

Cost impact: at 98 Tier 2 sources with ~15K input tokens each, skipping
even 60% of unchanged sources saves ~$0.24/week in GPT-4o-mini costs.

Usage (in handler.py):
    cache = SourceCache()
    cache.load()                        # one DB query at startup

    scraper._source_cache = cache       # attach before calling .scrape()
    events = scraper.scrape()           # skips GPT if content unchanged

    cache.save()                        # one bulk upsert at end of run
"""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)


class SourceCache:
    """Per-source content hash cache backed by Supabase scraper_source_cache."""

    def __init__(self) -> None:
        self._url = os.getenv("SUPABASE_URL", "")
        self._key = os.getenv("SUPABASE_SERVICE_KEY", "")
        self._hashes: dict[str, str] = {}   # source_name → hash
        self._updates: list[dict] = []

    def _headers(self) -> dict:
        return {
            "apikey":        self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type":  "application/json",
        }

    # ── Public API ──────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Fetch all cached hashes from Supabase (one query at scraper start)."""
        if not self._url or not self._key:
            logger.warning("Supabase not configured — content cache disabled")
            return
        try:
            resp = httpx.get(
                f"{self._url}/rest/v1/scraper_source_cache"
                "?select=source_name,content_hash",
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            for row in resp.json():
                self._hashes[row["source_name"]] = row["content_hash"]
            logger.info("Source cache loaded: %d entries", len(self._hashes))
        except Exception as exc:
            logger.warning("Failed to load source cache (continuing without): %s", exc)

    def has_changed(self, source_name: str, cleaned_content: str) -> bool:
        """Return True if content differs from cached hash — or no cached entry yet."""
        new_hash = _sha256(cleaned_content)
        return self._hashes.get(source_name) != new_hash

    def mark_scraped(self, source_name: str, cleaned_content: str, events_found: int) -> None:
        """Record that a source was successfully scraped with this content."""
        h = _sha256(cleaned_content)
        self._hashes[source_name] = h          # update local copy
        self._updates.append({
            "source_name":     source_name,
            "content_hash":    h,
            "last_scraped_at": datetime.now(timezone.utc).isoformat(),
            "events_found":    events_found,
        })

    def save(self) -> None:
        """Bulk-upsert all updates back to Supabase (one query at scraper end)."""
        if not self._updates or not self._url or not self._key:
            return
        try:
            resp = httpx.post(
                f"{self._url}/rest/v1/scraper_source_cache?on_conflict=source_name",
                json=self._updates,
                headers={
                    **self._headers(),
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
                timeout=15,
            )
            resp.raise_for_status()
            logger.info("Source cache saved: %d updates", len(self._updates))
        except Exception as exc:
            logger.warning("Failed to save source cache: %s", exc)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()
