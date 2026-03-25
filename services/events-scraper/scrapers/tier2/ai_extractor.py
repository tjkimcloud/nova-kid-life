"""
Tier 2 — AI-powered event extractor.
Fetches any URL, cleans the HTML, and uses gpt-4o-mini to extract
structured events. Works even when HTML structure changes or is irregular.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

from openai import OpenAI

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

_client: OpenAI | None = None

def _build_system_prompt() -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""You are a family events data extractor for NovaKidLife,
a Northern Virginia family events platform. Today's date is {today}.

Extract ONLY upcoming family-relevant events (start_at >= {today}) from the
provided page content. Do NOT extract events that have already passed.
Focus on events for children and families in Northern Virginia.

Respond ONLY with a JSON array of event objects. If no upcoming family events
are found, respond with an empty array [].

Each event object must have these fields:
{{
  "title": "event title (string)",
  "start_at": "ISO 8601 datetime (YYYY-MM-DDTHH:MM:SS) — if year not shown, use {today[:4]}",
  "end_at": "ISO 8601 datetime or null",
  "description": "event description (string)",
  "location_text": "city/venue, VA (string)",
  "venue_name": "venue name (string)",
  "is_free": true/false,
  "cost_description": "e.g. '$5/person' or 'Free' (string)",
  "age_range": "e.g. '3-8 years' or 'All ages' (string)",
  "tags": ["array", "of", "relevant", "tags"],
  "registration_url": "URL string or null",
  "image_url": "URL string or null"
}}"""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


class AIEventExtractor(BaseScraper):
    """
    Extracts events from any URL using gpt-4o-mini.
    Used as:
    1. Fallback when Tier 1 structured extraction fails
    2. Primary extractor for Tier 2 sources (dullesmoms.com, patch.com, etc.)
    """

    source_name = "ai-extractor"

    def __init__(self, source_name: str = "ai-extractor", **kwargs) -> None:
        super().__init__(**kwargs)
        self.source_name = source_name

    def scrape(self) -> list[RawEvent]:
        # AIEventExtractor is called directly with a URL, not via scrape()
        return []

    def extract_from_url(self, url: str, extra_context: str = "") -> list[RawEvent]:
        """Fetch a URL and extract events using AI."""
        logger.info("[%s] AI extracting from %s", self.source_name, url)
        try:
            html = self._fetch(url)
            return self.extract_from_html(html, source_url=url, extra_context=extra_context)
        except Exception as exc:
            logger.error("[%s] Failed to fetch %s: %s", self.source_name, url, exc)
            return []

    def extract_from_html(
        self,
        html: str,
        source_url: str,
        extra_context: str = "",
    ) -> list[RawEvent]:
        """Extract events from raw HTML using AI."""
        cleaned = self._clean_html(html, max_chars=80_000)

        user_message = f"Source URL: {source_url}\n"
        if extra_context:
            user_message += f"Context: {extra_context}\n"
        user_message += f"\nPage content:\n{cleaned}"

        try:
            response = _get_client().chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _build_system_prompt()},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=4000,
                temperature=0,
            )
            raw = json.loads(response.choices[0].message.content)
            items = raw if isinstance(raw, list) else raw.get("events", [])
            events = []
            for item in items:
                try:
                    events.append(self._to_raw_event(item, source_url))
                except Exception as exc:
                    logger.debug("Skipping AI event: %s", exc)
            logger.info("[%s] AI extracted %d events from %s", self.source_name, len(events), source_url)
            return events
        except Exception as exc:
            logger.error("[%s] AI extraction failed for %s: %s", self.source_name, source_url, exc)
            return []

    def _to_raw_event(self, item: dict, source_url: str) -> RawEvent:
        start_str = item.get("start_at", "")
        if not start_str:
            raise ValueError("No start_at")

        # If no timezone, assume Eastern
        if "T" in start_str and "+" not in start_str and "Z" not in start_str:
            start_str += "-05:00"
        start_at = datetime.fromisoformat(start_str)

        end_at = None
        end_str = item.get("end_at", "")
        if end_str:
            if "T" in end_str and "+" not in end_str and "Z" not in end_str:
                end_str += "-05:00"
            end_at = datetime.fromisoformat(end_str)

        return RawEvent(
            title=item.get("title", "").strip(),
            source_url=item.get("registration_url") or source_url,
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=item.get("description", ""),
            location_text=item.get("location_text", ""),
            venue_name=item.get("venue_name", ""),
            is_free=bool(item.get("is_free", False)),
            cost_description=item.get("cost_description", ""),
            age_range=item.get("age_range", ""),
            tags=item.get("tags", []),
            registration_url=item.get("registration_url", ""),
            image_url=item.get("image_url", "") or "",
            event_type=EventType.EVENT,
        )


class AITier2Scraper(BaseScraper):
    """
    Config-driven Tier 2 scraper.
    Instantiated from sources.json entries with a 'url' field.
    No custom code needed — just add a JSON entry.

    Attach a SourceCache before calling scrape() to skip GPT when content
    hasn't changed since the last run:
        scraper._source_cache = cache
    """

    def __init__(self, source_name: str, url: str, tags: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source_name = source_name
        self.url = url
        self.extra_tags = tags or []
        self._extractor = AIEventExtractor(source_name=source_name)
        self._source_cache = None  # set by handler.py before scrape()

    def scrape(self) -> list[RawEvent]:
        logger.info("[%s] Tier 2 AI scrape of %s", self.source_name, self.url)

        # Fetch and clean HTML first so we can hash-check before calling GPT
        try:
            html = self._fetch(self.url)
        except Exception as exc:
            logger.error("[%s] Failed to fetch %s: %s", self.source_name, self.url, exc)
            return []

        cleaned = self._extractor._clean_html(html, max_chars=80_000)

        # Skip GPT extraction if page content hasn't changed
        cache = self._source_cache
        if cache and not cache.has_changed(self.source_name, cleaned):
            logger.info("[%s] Content unchanged — skipping GPT extraction", self.source_name)
            return []

        events = self._extractor.extract_from_html(html, source_url=self.url)

        if cache:
            cache.mark_scraped(self.source_name, cleaned, len(events))

        # Inject config-level tags
        if self.extra_tags:
            for event in events:
                event.tags = list(set(event.tags + self.extra_tags))

        return events
