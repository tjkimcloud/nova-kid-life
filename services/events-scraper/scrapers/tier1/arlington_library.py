"""
Tier 1 scraper — Arlington Public Library events.
"""
from __future__ import annotations

import logging
from datetime import datetime

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

# arlingtonva.libcal.com/events is 404; use library website for AI fallback
# api_events.php (legacy) returns empty
_BASE_URL = "https://library.arlingtonva.us/events/"
_LIBCAL_API = "https://arlingtonva.libcal.com/api_events.php"


class ArlingtonLibraryScraper(BaseScraper):
    source_name = "arlington-library"

    def scrape(self) -> list[RawEvent]:
        logger.info("[%s] Starting scrape", self.source_name)

        for strategy in [self._scrape_libcal, self._scrape_json_ld]:
            try:
                events = strategy()
                if events:
                    return events
            except Exception as exc:
                logger.warning("[%s] Strategy failed: %s", self.source_name, exc)

        from ..tier2.ai_extractor import AIEventExtractor
        return AIEventExtractor(source_name=self.source_name).extract_from_url(_BASE_URL)

    def _scrape_libcal(self) -> list[RawEvent]:
        data = self._fetch_json(f"{_LIBCAL_API}?limit=100&cal_id=0")
        items = data if isinstance(data, list) else data.get("events", [])
        events = []
        for item in items:
            try:
                start_at = datetime.fromisoformat(item.get("start", "").replace("Z", "+00:00"))
                end_str = item.get("end", "")
                end_at = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None
                location = item.get("location", {})
                venue = location.get("name", "") if isinstance(location, dict) else str(location)
                events.append(RawEvent(
                    title=item.get("title", "").strip(),
                    source_url=item.get("url", _BASE_URL),
                    source_name=self.source_name,
                    start_at=start_at,
                    end_at=end_at,
                    description=item.get("description", ""),
                    venue_name=venue,
                    location_text=f"{venue}, Arlington, VA".strip(", "),
                    is_free=True,
                    event_type=EventType.EVENT,
                    tags=["library", "arlington"],
                    age_range=item.get("audience", ""),
                ))
            except Exception as exc:
                logger.debug("Skipping event: %s", exc)
        return events

    def _scrape_json_ld(self) -> list[RawEvent]:
        html = self._fetch(_BASE_URL)
        items = self._extract_json_ld(html)
        events = []
        for item in items:
            try:
                start_at = datetime.fromisoformat(item.get("startDate", "").replace("Z", "+00:00"))
                location = item.get("location", {})
                venue = location.get("name", "") if isinstance(location, dict) else ""
                events.append(RawEvent(
                    title=item.get("name", "").strip(),
                    source_url=item.get("url", _BASE_URL),
                    source_name=self.source_name,
                    start_at=start_at,
                    description=item.get("description", ""),
                    venue_name=venue,
                    location_text=f"{venue}, Arlington, VA".strip(", "),
                    is_free=True,
                    event_type=EventType.EVENT,
                    tags=["library", "arlington"],
                ))
            except Exception as exc:
                logger.debug("Skipping: %s", exc)
        return events
