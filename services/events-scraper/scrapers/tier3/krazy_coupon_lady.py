"""
Tier 3 — KrazyCouponLady restaurant and food deal scraper.
Scrapes krazycouponlady.com/deals/restaurants/ — the website version of
the content KrazyCouponLady posts on Instagram/social media.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone

from openai import OpenAI

from ..base import BaseScraper
from ..models import DealCategory, EventType, RawEvent

logger = logging.getLogger(__name__)

_URLS = [
    "https://www.krazycouponlady.com/deals/restaurants",
    "https://www.krazycouponlady.com/tips/food/free-food-deals",
    "https://www.krazycouponlady.com/deals/freebies",
]

_SYSTEM_PROMPT = """Extract all restaurant and food deals from this page.
Return a JSON array of deal objects. Empty array if none found.

Each deal:
{
  "title": "deal title",
  "brand": "restaurant/brand name",
  "discount_description": "what the deal is",
  "description": "full details including any promo codes or conditions",
  "url": "direct deal URL if available",
  "is_free": true/false,
  "valid_until": "YYYY-MM-DD or null",
  "tags": ["array", "of", "tags"]
}"""


class KrazyCouponLadyScraper(BaseScraper):
    source_name = "krazy-coupon-lady"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

    def scrape(self) -> list[RawEvent]:
        all_deals: list[RawEvent] = []

        for url in _URLS:
            try:
                deals = self._scrape_page(url)
                all_deals.extend(deals)
                logger.info("[%s] %s → %d deals", self.source_name, url, len(deals))
            except Exception as exc:
                logger.warning("[%s] Failed %s: %s", self.source_name, url, exc)

        return all_deals

    def _scrape_page(self, url: str) -> list[RawEvent]:
        html = self._fetch(url)
        cleaned = self._clean_html(html, max_chars=60_000)

        response = self._openai.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"URL: {url}\n\n{cleaned}"},
            ],
            max_tokens=3000,
            temperature=0,
        )

        raw = json.loads(response.choices[0].message.content)
        items = raw if isinstance(raw, list) else raw.get("deals", [])

        deals = []
        now = datetime.now(timezone.utc)

        for item in items:
            try:
                valid_until = None
                if item.get("valid_until"):
                    try:
                        valid_until = datetime.fromisoformat(item["valid_until"])
                    except ValueError:
                        pass

                deals.append(RawEvent(
                    title=item.get("title", "")[:120],
                    source_url=item.get("url") or url,
                    source_name=self.source_name,
                    start_at=now,
                    end_at=valid_until,
                    description=item.get("description", ""),
                    is_free=bool(item.get("is_free", False)),
                    event_type=EventType.DEAL,
                    deal_category=DealCategory.RESTAURANT,
                    brand=item.get("brand", ""),
                    discount_description=item.get("discount_description", ""),
                    tags=item.get("tags", ["deal", "restaurant", "food"]),
                ))
            except Exception as exc:
                logger.debug("Skipping deal: %s", exc)

        return deals
