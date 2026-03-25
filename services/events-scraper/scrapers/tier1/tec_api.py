"""
Tier 1 — The Events Calendar (TEC / tribe) REST API scraper.

Many Northern Virginia community sites run The Events Calendar WordPress plugin,
which exposes a REST API at /wp-json/tribe/events/v1/events.

This module provides a reusable base class + per-site subclasses.
Currently supported:
  - Prince William Living (princewilliamliving.com) — 228 events, PW County
  - DC Area Moms / DCMoms (dcmoms.com) — VA-filtered events
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

# TEC API parameters
_PER_PAGE = 50
_MAX_PAGES = 4  # 200 events max per site — plenty for upcoming events


class TECApiScraper(BaseScraper):
    """
    Generic scraper for any site running The Events Calendar WordPress plugin.
    Hits the /wp-json/tribe/events/v1/events REST endpoint.

    Subclasses set:
        source_name: str
        _api_url: str
        _state_filter: str | None  — if set, only include events in this state
        _tags: list[str]
    """

    source_name: str = ""
    _api_url: str = ""
    _state_filter: str | None = None
    _tags: list[str] = []

    def scrape(self) -> list[RawEvent]:
        logger.info("[%s] Fetching TEC API: %s", self.source_name, self._api_url)
        events: list[RawEvent] = []
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        page = 1
        while page <= _MAX_PAGES:
            url = (
                f"{self._api_url}"
                f"?start_date={today}"
                f"&per_page={_PER_PAGE}"
                f"&page={page}"
            )
            try:
                data = self._fetch_json(url)
            except Exception as exc:
                logger.warning("[%s] TEC API page %d failed: %s", self.source_name, page, exc)
                break

            raw_events = data.get("events", []) if isinstance(data, dict) else data
            if not raw_events:
                break

            for item in raw_events:
                try:
                    event = self._parse_event(item)
                    if event:
                        events.append(event)
                except Exception as exc:
                    logger.debug("[%s] Skipping event: %s", self.source_name, exc)

            # Check if there are more pages
            total_pages = data.get("total_pages", 1) if isinstance(data, dict) else 1
            if page >= total_pages:
                break
            page += 1

        logger.info("[%s] TEC API returned %d events", self.source_name, len(events))
        return events

    def _parse_event(self, item: dict) -> RawEvent | None:
        """Parse a TEC API event object into a RawEvent."""
        title = (item.get("title") or "").strip()
        if not title:
            return None

        # Dates — TEC returns "YYYY-MM-DD HH:MM:SS" in local timezone
        start_str = item.get("start_date", "")
        end_str = item.get("end_date", "")
        if not start_str:
            return None

        # Parse as UTC (TEC doesn't include timezone in start_date; treat as local ET)
        try:
            start_at = datetime.fromisoformat(start_str).replace(tzinfo=timezone.utc)
        except ValueError:
            return None
        end_at = None
        if end_str:
            try:
                end_at = datetime.fromisoformat(end_str).replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        # Skip past events
        now = datetime.now(timezone.utc)
        if start_at < now:
            return None

        # Venue / location
        venue = item.get("venue") or {}
        venue_name = venue.get("venue", "") or ""
        city = venue.get("city", "") or ""
        state = venue.get("stateprovince", "") or venue.get("state", "") or ""
        zip_code = venue.get("zip", "") or ""
        address = venue.get("address", "") or ""

        # Geo-filter: skip events outside the target state
        if self._state_filter and state and state.upper() != self._state_filter.upper():
            return None

        full_address = f"{address}, {city}, {state} {zip_code}".strip(", ").strip()
        location_text = f"{venue_name}, {city}, {state}".strip(", ") if venue_name else f"{city}, {state}".strip(", ")

        # Cost
        cost_raw = (item.get("cost") or "").strip()
        is_free = cost_raw.lower() in ("", "free", "0", "$0", "no cost", "free admission")

        # Tags from TEC categories + tags
        tags = list(self._tags)
        for cat in item.get("categories", []):
            tag = (cat.get("name") or "").lower().strip()
            if tag and tag not in tags:
                tags.append(tag)

        # Description — TEC returns HTML; strip tags for plain text
        desc_html = item.get("description") or ""
        from bs4 import BeautifulSoup
        description = BeautifulSoup(desc_html, "html.parser").get_text(separator=" ").strip()[:2000]

        url = item.get("url") or self._api_url

        return RawEvent(
            title=title[:120],
            source_url=url,
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=description,
            venue_name=venue_name,
            address=full_address,
            location_text=location_text,
            is_free=is_free,
            cost_description=cost_raw if not is_free else "",
            event_type=EventType.EVENT,
            tags=tags,
        )


class PWLivingScraper(TECApiScraper):
    """Prince William Living — community events magazine for Prince William County, VA."""
    source_name = "pw-living"
    _api_url = "https://princewilliamliving.com/wp-json/tribe/events/v1/events"
    _state_filter = "VA"
    _tags = ["prince-william", "community", "nova"]


class DCMomsScraper(TECApiScraper):
    """DC Area Moms — geo-filtered to Virginia events only."""
    source_name = "dc-moms"
    _api_url = "https://dcmoms.com/wp-json/tribe/events/v1/events"
    _state_filter = "VA"
    _tags = ["community", "nova", "family"]
