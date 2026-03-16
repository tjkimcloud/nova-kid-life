"""
Tier 1 scraper — Eventbrite family/kids events in Northern Virginia.
Uses Eventbrite's public search page with JSON-LD extraction.
"""
from __future__ import annotations

import logging
from datetime import datetime

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

# Eventbrite search: family events in Northern Virginia
_SEARCH_URLS = [
    "https://www.eventbrite.com/d/va--fairfax/family--children-events/",
    "https://www.eventbrite.com/d/va--ashburn/family--children-events/",
    "https://www.eventbrite.com/d/va--arlington/family--children-events/",
    "https://www.eventbrite.com/d/va--reston/family--children-events/",
    "https://www.eventbrite.com/d/va--leesburg/family--children-events/",
]

_FAMILY_KEYWORDS = {
    "kid", "child", "family", "toddler", "baby", "parent",
    "teen", "youth", "junior", "storytime", "craft", "playdate",
}


class EventbriteNovaScraper(BaseScraper):
    source_name = "eventbrite-nova"

    def scrape(self) -> list[RawEvent]:
        logger.info("[%s] Starting scrape across %d URLs", self.source_name, len(_SEARCH_URLS))
        seen_urls: set[str] = set()
        all_events: list[RawEvent] = []

        for search_url in _SEARCH_URLS:
            try:
                events = self._scrape_page(search_url, seen_urls)
                all_events.extend(events)
                logger.info("[%s] %s → %d events", self.source_name, search_url, len(events))
            except Exception as exc:
                logger.warning("[%s] Failed to scrape %s: %s", self.source_name, search_url, exc)

        logger.info("[%s] Total: %d unique events", self.source_name, len(all_events))
        return all_events

    def _scrape_page(self, url: str, seen_urls: set[str]) -> list[RawEvent]:
        html = self._fetch(url)

        # Eventbrite embeds rich JSON-LD Event objects
        json_ld_events = self._extract_json_ld(html)

        # Also try parsing the search results listing
        events: list[RawEvent] = []

        for item in json_ld_events:
            try:
                event_url = item.get("url", "")
                if event_url in seen_urls:
                    continue
                seen_urls.add(event_url)

                event = self._parse_json_ld(item)
                if self._is_family_relevant(event):
                    events.append(event)
            except Exception as exc:
                logger.debug("Skipping Eventbrite event: %s", exc)

        return events

    def _parse_json_ld(self, item: dict) -> RawEvent:
        start_at = datetime.fromisoformat(item.get("startDate", "").replace("Z", "+00:00"))
        end_str = item.get("endDate", "")
        end_at = datetime.fromisoformat(end_str.replace("Z", "+00:00")) if end_str else None

        location = item.get("location", {})
        venue_name = location.get("name", "") if isinstance(location, dict) else ""
        address_obj = location.get("address", {}) if isinstance(location, dict) else {}
        if isinstance(address_obj, dict):
            city = address_obj.get("addressLocality", "")
            state = address_obj.get("addressRegion", "")
            street = address_obj.get("streetAddress", "")
            location_text = f"{city}, {state}".strip(", ") if city else "Northern Virginia"
            address = f"{street}, {city}, {state}".strip(", ")
        else:
            location_text = "Northern Virginia"
            address = ""

        offers = item.get("offers", {})
        is_free = False
        cost_desc = ""
        if isinstance(offers, dict):
            price = offers.get("price", "")
            is_free = str(price) in ("0", "0.00", "Free", "")
            if not is_free and price:
                cost_desc = f"From ${price}"

        organizer = item.get("organizer", {})
        organizer_name = organizer.get("name", "") if isinstance(organizer, dict) else ""

        return RawEvent(
            title=item.get("name", "").strip(),
            source_url=item.get("url", ""),
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=item.get("description", ""),
            venue_name=venue_name,
            address=address,
            location_text=location_text,
            is_free=is_free,
            cost_description=cost_desc,
            image_url=item.get("image", ""),
            event_type=EventType.EVENT,
            tags=["eventbrite", "northern-virginia"],
        )

    def _is_family_relevant(self, event: RawEvent) -> bool:
        text = (event.title + " " + event.description).lower()
        return any(kw in text for kw in _FAMILY_KEYWORDS)
