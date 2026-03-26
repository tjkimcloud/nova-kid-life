"""
Tier 1 — The Events Calendar (TEC / tribe) scrapers.

Many Northern Virginia community sites run The Events Calendar WordPress plugin.
Two scraping strategies:

1. TECApiScraper  — hits /wp-json/tribe/events/v1/events REST endpoint.
   Fast and structured; blocked by some WAFs.

2. TECHtmlScraper — parses Schema.org JSON-LD embedded in list calendar pages.
   Works even when REST API is blocked; follows next_url pagination.
   Config-driven: add "parser": "tec_html" to a tier2_events entry.

Currently supported:
  REST API:  DC Area Moms / DCMoms (dcmoms.com) — VA-filtered
  HTML:      DullesMoms (via dedicated DullesMomsScraper in dullesmoms.py)
             Fairfax Family Fun, The Loudoun Moms, Nova Moms Blog, ...
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup

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


# ── Generic TEC HTML scraper ───────────────────────────────────────────────────

class TECHtmlScraper(BaseScraper):
    """
    Config-driven scraper for any site running The Events Calendar WordPress plugin.

    Instead of the REST API, this fetches the HTML list calendar page and parses
    the Schema.org JSON-LD blocks embedded by TEC — same technique as DullesMomsScraper
    but instantiated from sources.json config (no code changes to add new sites).

    Usage in sources.json tier2_events entry:
        { "name": "...", "url": "https://site.com/events/list/",
          "parser": "tec_html", "tags": [...], "enabled": true }

    Optional config fields:
        "max_pages": 6          # default 6 (≈120 events per run)
        "state_filter": "VA"    # skip events outside this state (from address)
    """

    def __init__(
        self,
        source_name: str,
        url: str,
        tags: list[str] | None = None,
        max_pages: int = 6,
        state_filter: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.source_name = source_name
        self.url = url
        self.extra_tags = tags or []
        self._max_pages = max_pages
        self._state_filter = state_filter.upper() if state_filter else None

    # ── Public API ─────────────────────────────────────────────────────────────

    def scrape(self) -> list[RawEvent]:
        events: list[RawEvent] = []
        url: str | None = self.url
        pages_fetched = 0

        while url and pages_fetched < self._max_pages:
            try:
                html = self._fetch(url)
            except Exception as exc:
                logger.warning("[%s] Failed to fetch %s: %s", self.source_name, url, exc)
                break

            page_events = self._parse_page(html)
            events.extend(page_events)
            logger.info(
                "[%s] Page %d (%s): %d events",
                self.source_name, pages_fetched + 1, url, len(page_events),
            )

            url = self._next_url(html)
            pages_fetched += 1

        now = datetime.now(timezone.utc)
        upcoming = [e for e in events if e.start_at >= now]
        logger.info(
            "[%s] Total: %d scraped, %d upcoming",
            self.source_name, len(events), len(upcoming),
        )
        return upcoming

    # ── HTML parsing ───────────────────────────────────────────────────────────

    def _parse_page(self, html: str) -> list[RawEvent]:
        json_ld_items = self._extract_json_ld(html)
        events = []
        for item in json_ld_items:
            try:
                event = self._parse_schema_event(item)
                if event:
                    events.append(event)
            except Exception as exc:
                logger.debug("[%s] Skipping event: %s", self.source_name, exc)
        return events

    def _parse_schema_event(self, item: dict) -> RawEvent | None:
        title = (item.get("name") or "").strip()
        if not title:
            return None

        start_str = item.get("startDate", "")
        if not start_str:
            return None
        try:
            start_at = datetime.fromisoformat(start_str)
            if start_at.tzinfo is None:
                start_at = start_at.replace(tzinfo=timezone.utc)
        except ValueError:
            return None

        end_at = None
        end_str = item.get("endDate", "")
        if end_str:
            try:
                end_at = datetime.fromisoformat(end_str)
                if end_at.tzinfo is None:
                    end_at = end_at.replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        # Location
        location = item.get("location") or {}
        venue_name = location.get("name", "") if isinstance(location, dict) else ""
        addr_obj = location.get("address", {}) if isinstance(location, dict) else {}
        if isinstance(addr_obj, dict):
            street  = addr_obj.get("streetAddress", "")
            city    = addr_obj.get("addressLocality", "")
            state   = addr_obj.get("addressRegion", "")
            zipcode = addr_obj.get("postalCode", "")
            address = f"{street}, {city}, {state} {zipcode}".strip(", ").strip()
        else:
            address = str(addr_obj)
            city = ""
            state = ""

        # Geo-filter
        if self._state_filter and state and state.upper() != self._state_filter:
            return None

        location_text = (
            f"{venue_name}, {city}, {state}".strip(", ")
            if venue_name else f"{city}, {state}".strip(", ")
        )

        # Description — strip HTML
        desc_html = item.get("description") or ""
        description = BeautifulSoup(desc_html, "html.parser").get_text(separator=" ").strip()[:2000]

        # Cost from description heuristic + offers block
        is_free = any(
            w in description.lower()[:200]
            for w in ("free", "no cost", "no charge", "free admission")
        )
        offers = item.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        if isinstance(offers, dict) and offers.get("price") in (0, "0", "", "Free", "free"):
            is_free = True

        tags = list(self.extra_tags)

        event_url = item.get("url") or self.url

        return RawEvent(
            title=title[:120],
            source_url=event_url,
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=description,
            venue_name=venue_name,
            address=address,
            location_text=location_text,
            is_free=is_free,
            event_type=EventType.EVENT,
            tags=tags,
        )

    def _next_url(self, html: str) -> str | None:
        """Extract the next page URL from the TEC view-state JSON block."""
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            text = script.string or ""
            if '"next_url"' in text and '"events"' in text:
                try:
                    data = json.loads(text)
                    next_url = data.get("next_url")
                    if next_url and isinstance(next_url, str):
                        return next_url
                except (json.JSONDecodeError, AttributeError):
                    m = re.search(r'"next_url"\s*:\s*"([^"]+)"', text)
                    if m:
                        return m.group(1)
        return None
