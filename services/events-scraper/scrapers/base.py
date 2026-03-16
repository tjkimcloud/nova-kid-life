"""
Abstract base class for all scrapers.
Provides shared HTTP fetching, HTML cleaning, and slug generation.
"""
from __future__ import annotations

import hashlib
import logging
import re
import time
from abc import ABC, abstractmethod

import httpx
from bs4 import BeautifulSoup

from .models import RawEvent

logger = logging.getLogger(__name__)

# Spoof a real browser to avoid trivial bot blocks
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# HTML tags to strip before sending to AI (reduces tokens)
_STRIP_TAGS = {
    "script", "style", "noscript", "iframe", "svg",
    "nav", "footer", "header", "aside", "form",
    "button", "input", "meta", "link",
}


class BaseScraper(ABC):
    """
    All scrapers inherit from this class.

    Subclasses must define:
      source_name: str          — unique identifier stored in events.source_name
      scrape() -> list[RawEvent]
    """

    source_name: str = ""

    def __init__(self, timeout: int = 30, max_retries: int = 3) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(
            headers=_HEADERS,
            timeout=timeout,
            follow_redirects=True,
        )

    def __del__(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

    @abstractmethod
    def scrape(self) -> list[RawEvent]:
        """Fetch and return raw events/deals from this source."""

    # ── HTTP helpers ──────────────────────────────────────────────────────────

    def _fetch(self, url: str) -> str:
        """GET a URL with retries. Returns HTML text or raises."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._client.get(url)
                resp.raise_for_status()
                return resp.text
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning("Rate limited by %s — waiting %ss", url, wait)
                    time.sleep(wait)
                    last_exc = exc
                elif exc.response.status_code in (403, 404):
                    raise  # Don't retry permanent errors
                else:
                    last_exc = exc
            except httpx.RequestError as exc:
                logger.warning("Request error (attempt %d): %s", attempt, exc)
                last_exc = exc
                time.sleep(attempt)

        raise last_exc or RuntimeError(f"Failed to fetch {url}")

    def _fetch_json(self, url: str) -> dict | list:
        """GET a JSON endpoint."""
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._client.get(url)
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                if attempt == self.max_retries:
                    raise
                time.sleep(attempt)
        raise RuntimeError(f"Failed to fetch JSON from {url}")

    # ── HTML helpers ──────────────────────────────────────────────────────────

    def _parse(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html.parser")

    def _clean_html(self, html: str, max_chars: int = 80_000) -> str:
        """
        Strip boilerplate tags and truncate for AI context windows.
        Keeps visible text content and semantic structure.
        """
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(_STRIP_TAGS):
            tag.decompose()

        # Collapse whitespace
        text = re.sub(r"\s{3,}", "\n\n", soup.get_text(separator="\n"))
        return text[:max_chars]

    def _extract_json_ld(self, html: str) -> list[dict]:
        """
        Extract Event objects from JSON-LD structured data.
        Many modern sites (Eventbrite, library systems) embed these.
        """
        import json

        soup = BeautifulSoup(html, "html.parser")
        results = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    results.extend(d for d in data if d.get("@type") == "Event")
                elif isinstance(data, dict):
                    if data.get("@type") == "Event":
                        results.append(data)
                    # Handle @graph arrays
                    for item in data.get("@graph", []):
                        if item.get("@type") == "Event":
                            results.append(item)
            except (json.JSONDecodeError, AttributeError):
                continue
        return results

    # ── Utility helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _to_slug(text: str, suffix: str = "") -> str:
        """Generate a URL-safe slug from text."""
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
        if suffix:
            slug = f"{slug}-{suffix}"
        return slug[:120]

    @staticmethod
    def _url_hash(url: str) -> str:
        """Short hash of a URL — used as slug suffix for deduplication."""
        return hashlib.md5(url.encode()).hexdigest()[:8]
