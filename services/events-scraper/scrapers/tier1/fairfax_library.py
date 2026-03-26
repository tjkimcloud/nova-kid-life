"""
Tier 1 scraper — Fairfax County Public Library events.
Fairfax uses Springshare LibCal for event management.
Attempts JSON-LD extraction first, falls back to AI extraction.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

# Fairfax County Library uses Springshare LibCal at a custom domain.
# fairfaxcounty.libcal.com redirects → librarycalendar.fairfaxcounty.gov
# api_events.php (legacy) returns empty; HTML calendar used for AI fallback.
_BASE_URL = "https://librarycalendar.fairfaxcounty.gov/"
_LIBCAL_API = "https://librarycalendar.fairfaxcounty.gov/api_events.php"


class FairfaxLibraryScraper(BaseScraper):
    source_name = "fairfax-library"

    def scrape(self) -> list[RawEvent]:
        logger.info("[%s] Starting scrape", self.source_name)
        events: list[RawEvent] = []

        # Strategy 1: LibCal JSON API (returns structured data, most reliable)
        try:
            events = self._scrape_libcal()
            if events:
                logger.info("[%s] LibCal API returned %d events", self.source_name, len(events))
                return events
        except Exception as exc:
            logger.warning("[%s] LibCal API failed: %s — trying HTML", self.source_name, exc)

        # Strategy 2: JSON-LD structured data on the events page
        try:
            events = self._scrape_json_ld()
            if events:
                logger.info("[%s] JSON-LD extraction returned %d events", self.source_name, len(events))
                return events
        except Exception as exc:
            logger.warning("[%s] JSON-LD failed: %s — trying AI", self.source_name, exc)

        # Strategy 3: AI extraction (fallback — costs ~$0.001/page)
        try:
            from ..tier2.ai_extractor import AIEventExtractor
            extractor = AIEventExtractor(source_name=self.source_name)
            events = extractor.extract_from_url(_BASE_URL)
            logger.info("[%s] AI extraction returned %d events", self.source_name, len(events))
        except Exception as exc:
            logger.error("[%s] All extraction strategies failed: %s", self.source_name, exc)

        return events

    def _scrape_libcal(self) -> list[RawEvent]:
        """Try LibCal JSON API."""
        params = "?limit=100&cal_id=0&category=&audience=&tag=kids,children,family,toddler,teen"
        data = self._fetch_json(f"{_LIBCAL_API}{params}")

        events = []
        if not isinstance(data, list):
            data = data.get("events", [])

        for item in data:
            try:
                events.append(self._parse_libcal_event(item))
            except Exception as exc:
                logger.debug("Skipping LibCal event: %s", exc)

        return events

    def _parse_libcal_event(self, item: dict) -> RawEvent:
        start_str = item.get("start") or item.get("start_dt", "")
        end_str = item.get("end") or item.get("end_dt", "")

        start_at = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end_at = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None

        url = item.get("url") or item.get("registration_url") or _BASE_URL

        return RawEvent(
            title=item.get("title", "").strip(),
            source_url=url,
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=item.get("description", ""),
            location_text=item.get("location", {}).get("name", "") if isinstance(item.get("location"), dict) else str(item.get("location", "")),
            venue_name=item.get("location", {}).get("name", "") if isinstance(item.get("location"), dict) else "",
            is_free=item.get("registration", {}).get("fee", "0") in ("0", "", "Free", None) if isinstance(item.get("registration"), dict) else True,
            event_type=EventType.EVENT,
            tags=["library", "fairfax"],
            age_range=item.get("audience", ""),
        )

    def _scrape_json_ld(self) -> list[RawEvent]:
        """Extract events from JSON-LD structured data on the events page."""
        html = self._fetch(_BASE_URL)
        json_ld_events = self._extract_json_ld(html)

        events = []
        for item in json_ld_events:
            try:
                events.append(self._parse_json_ld_event(item))
            except Exception as exc:
                logger.debug("Skipping JSON-LD event: %s", exc)

        return events

    def _parse_json_ld_event(self, item: dict) -> RawEvent:
        start_str = item.get("startDate", "")
        end_str = item.get("endDate", "")

        start_at = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        end_at = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None

        location = item.get("location", {})
        venue_name = location.get("name", "") if isinstance(location, dict) else ""
        address_obj = location.get("address", {}) if isinstance(location, dict) else {}
        address = (
            f"{address_obj.get('streetAddress', '')} {address_obj.get('addressLocality', '')} {address_obj.get('addressRegion', '')}".strip()
            if isinstance(address_obj, dict) else str(address_obj)
        )

        offers = item.get("offers", {})
        is_free = False
        if isinstance(offers, dict):
            is_free = offers.get("price") in (0, "0", "Free", "") or offers.get("availability") == "Free"

        url = item.get("url") or _BASE_URL

        return RawEvent(
            title=item.get("name", "").strip(),
            source_url=url,
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=item.get("description", ""),
            venue_name=venue_name,
            address=address,
            location_text=f"{venue_name}, Fairfax County, VA".strip(", "),
            is_free=is_free,
            event_type=EventType.EVENT,
            tags=["library", "fairfax"],
            image_url=item.get("image", ""),
        )
