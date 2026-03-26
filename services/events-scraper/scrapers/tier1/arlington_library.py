"""
Tier 1 scraper — Arlington Public Library events.

Strategies (in order):
1. LibCal iCal feed  — plain text, not JS-rendered, most reliable
2. LibCal JSON API   — deprecated api_events.php (currently returns empty)
3. JSON-LD           — LibCal calendar page JSON-LD (JS-rendered, usually 0 events)
4. AI fallback       — library website HTML
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from ..base import BaseScraper
from ..models import EventType, RawEvent

logger = logging.getLogger(__name__)

# LibCal iCal feed — plain text, server-rendered, works without JavaScript
# api_events.php?out=ical returns iCal format even when JSON format is empty
_ICAL_URL = "https://arlingtonva.libcal.com/api_events.php?cal_id=0&limit=100&out=ical"
# LibCal API v1.1 — newer semi-public endpoint that may still work
_LIBCAL_API_V11 = "https://arlingtonva.libcal.com/api/1.1/events?limit=100&cal_id=0"
_LIBCAL_API = "https://arlingtonva.libcal.com/api_events.php?limit=100&cal_id=0"
_LIBCAL_CALENDAR_URL = "https://arlingtonva.libcal.com/calendar"
_BASE_URL = "https://library.arlingtonva.us/events/"


class ArlingtonLibraryScraper(BaseScraper):
    source_name = "arlington-library"

    def scrape(self) -> list[RawEvent]:
        logger.info("[%s] Starting scrape", self.source_name)

        # Strategy 1: iCal feed (plain text, no JS rendering needed)
        try:
            events = self._scrape_ical()
            if events:
                logger.info("[%s] iCal feed returned %d events", self.source_name, len(events))
                return events
        except Exception as exc:
            logger.warning("[%s] iCal strategy failed: %s", self.source_name, exc)

        # Strategy 2: LibCal API v1.1 (newer semi-public endpoint)
        try:
            events = self._scrape_libcal_v11()
            if events:
                logger.info("[%s] LibCal v1.1 API returned %d events", self.source_name, len(events))
                return events
        except Exception as exc:
            logger.warning("[%s] LibCal v1.1 strategy failed: %s", self.source_name, exc)

        # Strategy 3: LibCal JSON API (legacy, usually empty)
        try:
            events = self._scrape_libcal()
            if events:
                return events
        except Exception as exc:
            logger.warning("[%s] LibCal API strategy failed: %s", self.source_name, exc)

        # Strategy 3: JSON-LD on LibCal calendar page
        try:
            events = self._scrape_json_ld()
            if events:
                return events
        except Exception as exc:
            logger.warning("[%s] JSON-LD strategy failed: %s", self.source_name, exc)

        # Strategy 4: AI extraction on library website
        from ..tier2.ai_extractor import AIEventExtractor
        return AIEventExtractor(source_name=self.source_name).extract_from_url(_BASE_URL)

    def _scrape_ical(self) -> list[RawEvent]:
        """Parse the LibCal iCal feed — plain text, bypasses JS rendering."""
        ical_text = self._fetch(_ICAL_URL)
        if not ical_text or "BEGIN:VCALENDAR" not in ical_text:
            return []

        events = []
        vevent_re = re.compile(r"BEGIN:VEVENT(.*?)END:VEVENT", re.DOTALL)
        now = datetime.now(timezone.utc)

        for match in vevent_re.finditer(ical_text):
            try:
                vevent = match.group(1)
                event = self._parse_vevent(vevent, now)
                if event:
                    events.append(event)
            except Exception as exc:
                logger.debug("[%s] Skipping iCal event: %s", self.source_name, exc)

        return events

    def _parse_vevent(self, vevent: str, now: datetime) -> RawEvent | None:
        """Parse a single VEVENT block into a RawEvent."""

        def get(field: str) -> str:
            """Extract a field value, handling line folding."""
            m = re.search(
                rf"^{field}[;:](.*?)(?=\r?\n[^\s]|\Z)",
                vevent,
                re.MULTILINE | re.DOTALL,
            )
            if not m:
                return ""
            # Unfold continuation lines (RFC 5545: lines starting with space/tab)
            value = re.sub(r"\r?\n[ \t]", "", m.group(1)).strip()
            # Unescape common iCal text escapes
            return value.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")

        title = get("SUMMARY")
        if not title:
            return None

        start_str = get("DTSTART")
        if not start_str:
            return None

        start_at = _parse_ical_dt(start_str)
        if start_at is None or start_at < now:
            return None

        end_str = get("DTEND") or get("DURATION")
        end_at = _parse_ical_dt(end_str) if end_str and "T" in end_str else None

        url = get("URL") or _BASE_URL
        location = get("LOCATION")
        description = get("DESCRIPTION")

        return RawEvent(
            title=title[:120],
            source_url=url,
            source_name=self.source_name,
            start_at=start_at,
            end_at=end_at,
            description=description[:2000],
            venue_name=location,
            location_text=f"{location}, Arlington, VA".strip(", "),
            is_free=True,
            event_type=EventType.EVENT,
            tags=["library", "arlington"],
        )

    def _scrape_libcal_v11(self) -> list[RawEvent]:
        """Try the LibCal API v1.1 endpoint — newer, may still work without auth."""
        data = self._fetch_json(_LIBCAL_API_V11)
        events_list = data if isinstance(data, list) else data.get("events", [])
        events = []
        for item in events_list:
            try:
                start_str = item.get("start") or item.get("start_dt", "")
                end_str = item.get("end") or item.get("end_dt", "")
                start_at = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
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
                logger.debug("Skipping v1.1 event: %s", exc)
        return events

    def _scrape_libcal(self) -> list[RawEvent]:
        data = self._fetch_json(_LIBCAL_API)
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
        html = self._fetch(_LIBCAL_CALENDAR_URL)
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


def _parse_ical_dt(s: str) -> datetime | None:
    """Parse an iCal DTSTART/DTEND value into a timezone-aware datetime."""
    if not s:
        return None
    # Strip TZID or VALUE=DATE parameter prefix (e.g. TZID=America/New_York:20260401T...)
    if ":" in s:
        s = s.split(":", 1)[1]
    s = s.strip()
    try:
        if "T" in s:
            dt = datetime.strptime(s.rstrip("Z").replace("-", ""), "%Y%m%dT%H%M%S")
            if s.endswith("Z"):
                return dt.replace(tzinfo=timezone.utc)
            # Treat local time as Eastern (UTC-4 / UTC-5); use UTC as best approximation
            return dt.replace(tzinfo=timezone.utc)
        else:
            # Date-only: treat as midnight UTC
            return datetime.strptime(s, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
