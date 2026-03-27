"""
Tier 1 — DullesMoms.com calendar scraper.

DullesMoms uses The Events Calendar (tribe) WordPress plugin and embeds a
Schema.org JSON-LD array in every list page — 20 structured events per page
with full ISO timestamps, venue addresses, and descriptions.

This scraper bypasses the AI extractor entirely: it reads the JSON-LD directly,
paginating via the `next_url` in the TEC view-state JSON block.  Result: all
events, zero GPT cost, zero LLM filtering.

Calendar URL: https://dullesmoms.com/dmcalendar/list/
Pagination: follows next_url up to MAX_PAGES pages
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Iterator

from bs4 import BeautifulSoup

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

_BASE_URL = "https://dullesmoms.com/dmcalendar/list/"
_MAX_PAGES = 6   # 6 pages × 20 events = up to 120 events (≈ next 2 months)


class DullesMomsScraper(BaseScraper):
    source_name = "dullesmoms"

    def scrape(self) -> list[RawEvent]:
        events: list[RawEvent] = []
        url = _BASE_URL
        pages_fetched = 0

        while url and pages_fetched < _MAX_PAGES:
            try:
                html = self._fetch(url)
            except Exception as exc:
                logger.warning("[%s] Failed to fetch %s: %s", self.source_name, url, exc)
                break

            page_events = self._parse_page(html)
            events.extend(page_events)
            logger.info("[%s] Page %d (%s): %d events", self.source_name, pages_fetched + 1, url, len(page_events))

            url = self._next_url(html)
            pages_fetched += 1

        now = datetime.now(timezone.utc)
        upcoming = [e for e in events if e.start_at >= now]
        logger.info("[%s] Total: %d events scraped, %d upcoming", self.source_name, len(events), len(upcoming))
        return upcoming

    # ── HTML parsing ──────────────────────────────────────────────────────────

    def _parse_page(self, html: str) -> list[RawEvent]:
        """Extract all events from Schema.org JSON-LD embedded in the page."""
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
        """Parse a Schema.org Event object into a RawEvent."""
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
            state = "VA"

        location_text = f"{venue_name}, {city}, {state}".strip(", ") if venue_name else f"{city}, {state}".strip(", ")

        # Description — strip HTML tags
        desc_html = item.get("description") or ""
        description = BeautifulSoup(desc_html, "html.parser").get_text(separator=" ").strip()[:2000]

        # Cost — not in Schema.org for this site; check description for clues
        is_free = any(w in description.lower()[:200] for w in ("free", "no cost", "no charge", "free admission"))

        # Categories from URL path (e.g. dullesmoms.com/event-category/free-events/)
        url = item.get("url") or _BASE_URL
        tags = ["community", "nova"]

        # Offers block sometimes has price info
        offers = item.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        if isinstance(offers, dict):
            price = offers.get("price")
            if price in (0, "0", "", "Free", "free"):
                is_free = True

        # Try to extract the organizer's external event URL from the event page
        registration_url = self._get_external_event_url(url) if url and "dullesmoms.com" in url else None

        return RawEvent(
            title=title[:120],
            source_url=url,
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
            registration_url=registration_url or "",
        )

    def _get_external_event_url(self, event_page_url: str) -> str | None:
        """
        Fetch the individual dullesmoms event page and extract the external
        event website link (the organizer's own URL, not dullesmoms itself).
        Returns None if no external link is found or the fetch fails.
        """
        try:
            html = self._fetch(event_page_url)
        except Exception:
            return None

        soup = BeautifulSoup(html, "html.parser")

        # TEC renders an "Event Website" link with class tribe-event-url
        # or an <a> with rel="noopener" pointing off-site in the event meta.
        # Try several selectors in priority order.
        selectors = [
            "a.tribe-event-url",                # TEC "Event Website" anchor
            ".tribe-events-event-meta a[href]",  # any meta link
            ".tribe-venue-url a[href]",          # venue website
        ]
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                href = el.get("href", "")
                if href and "dullesmoms.com" not in href and href.startswith("http"):
                    return href

        # Fallback: any <a> in the event content that links off-site
        content = soup.select_one(".tribe-events-single, .tribe-events-content, article")
        if content:
            for a in content.find_all("a", href=True):
                href = a["href"]
                if (
                    href.startswith("http")
                    and "dullesmoms.com" not in href
                    and "facebook.com" not in href
                    and "google.com" not in href
                    and "instagram.com" not in href
                ):
                    return href

        return None

    def _next_url(self, html: str) -> str | None:
        """
        Extract the next page URL from the TEC view-state JSON block.
        The block is a <script> tag containing a JSON object with a 'next_url' key.
        """
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            text = script.string or ""
            # Look for the TEC view state block — starts with {"next_url":
            if '"next_url"' in text and '"events"' in text:
                try:
                    data = json.loads(text)
                    next_url = data.get("next_url")
                    if next_url and isinstance(next_url, str) and "dullesmoms.com" in next_url:
                        return next_url
                except (json.JSONDecodeError, AttributeError):
                    # Try regex fallback
                    m = re.search(r'"next_url"\s*:\s*"([^"]+)"', text)
                    if m:
                        return m.group(1)
        return None
