"""
Tier 3 — Google News RSS deal monitor.
Queries Google News RSS for viral deal keywords, fetches article content,
uses AI to extract structured deal data. Free, no API key required.
"""
from __future__ import annotations

import json
import logging
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import quote_plus

from openai import OpenAI

from ..base import BaseScraper
from ..models import DealCategory, EventType, RawEvent

logger = logging.getLogger(__name__)

_GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

_DEAL_SYSTEM_PROMPT = """You are a deal extractor for NovaKidLife, a Northern Virginia family platform.
Extract restaurant, food, and family-activity deals from news articles that are
AVAILABLE TO FAMILIES IN NORTHERN VIRGINIA / DC METRO AREA.

Respond with a JSON object. If no relevant deal is found, respond with {"found": false}.

── GEOGRAPHIC RULES (CRITICAL) ──────────────────────────────────────────────
Set "is_nova_available": true ONLY when:
  1. The brand has locations in the DC metro / Northern Virginia
     (e.g. Chipotle, McDonald's, IHOP, Olive Garden, Five Guys, Shake Shack,
      Chick-fil-A, Panera, Starbucks, Wendy's, Burger King, Dairy Queen, etc.)
  2. The deal is online-only or nationwide (apps, websites)

Set "is_nova_available": false when:
  - The deal is tied to a specific non-DMV sports team or stadium event
    (e.g. "Tigers", "Cubs", "Astros", "Saints" — these are not DC metro teams)
  - The deal is for a restaurant chain with no DC metro presence
  - The deal explicitly applies ONLY to locations in another city/region
  - The venue is a resort or attraction outside the DC metro area
    (e.g. Divi Resorts, regional amusement parks in other states)

── DATE RULES ───────────────────────────────────────────────────────────────
Provide accurate dates based on the article content.
A deal tied to a past holiday (Easter, Halloween, Thanksgiving, April Fools,
Burrito Day, etc.) that has already occurred should be flagged by setting
valid_until to that past date — the caller will skip expired deals.

If a deal is found:
{
  "found": true,
  "title": "short deal title (max 80 chars)",
  "brand": "restaurant or brand name",
  "discount_description": "what the deal is — e.g. 'BOGO entrée', 'Free burger on your birthday'",
  "description": "full deal description including any conditions",
  "is_free": true/false,
  "is_nova_available": true/false,
  "deal_category": "restaurant" | "activity" | "amusement" | "grocery" | "seasonal",
  "valid_from": "YYYY-MM-DD or null",
  "valid_until": "YYYY-MM-DD or null",
  "is_recurring": false,
  "tags": ["array", "of", "tags"]
}"""


class GoogleNewsRssScraper(BaseScraper):
    """
    Monitors Google News RSS for deal keywords.
    Fetches articles and uses AI to extract deal details.
    """

    source_name = "google-news-rss"

    def __init__(self, queries: list[str] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.queries = queries or ["restaurant deal", "free kids meal", "bogo food deal"]
        self._openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

    def scrape(self) -> list[RawEvent]:
        all_deals: list[RawEvent] = []
        seen_urls: set[str] = set()

        for query in self.queries:
            try:
                articles = self._fetch_rss(query)
                logger.info("[%s] Query '%s' → %d articles", self.source_name, query, len(articles))

                for article in articles[:5]:  # Limit per query to control cost
                    url = article.get("url", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    deal = self._extract_deal(article)
                    if deal:
                        all_deals.append(deal)

            except Exception as exc:
                logger.warning("[%s] Query '%s' failed: %s", self.source_name, query, exc)

        logger.info("[%s] Extracted %d deals total", self.source_name, len(all_deals))
        return all_deals

    def _fetch_rss(self, query: str) -> list[dict]:
        url = _GOOGLE_NEWS_RSS.format(query=quote_plus(query))
        xml_text = self._fetch(url)

        root = ET.fromstring(xml_text)
        articles = []

        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            description = item.findtext("description", "")

            articles.append({
                "title": title,
                "url": link,
                "published": pub_date,
                "snippet": description,
            })

        return articles

    def _extract_deal(self, article: dict) -> RawEvent | None:
        """Use AI to determine if article describes a relevant deal."""
        content = f"Headline: {article['title']}\nSnippet: {article['snippet']}"

        try:
            response = self._openai.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _DEAL_SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
                max_tokens=500,
                temperature=0,
            )
            data = json.loads(response.choices[0].message.content)

            if not data.get("found"):
                return None

            # Skip deals the AI flagged as not available in Northern Virginia
            if not data.get("is_nova_available", True):
                logger.info("[%s] Skipping non-NoVa deal: %s", self.source_name, data.get("title", article["title"]))
                return None

            # Parse valid dates
            now = datetime.now(timezone.utc)
            valid_from = now
            valid_until = None

            if data.get("valid_from"):
                try:
                    valid_from = datetime.fromisoformat(data["valid_from"])
                except ValueError:
                    pass

            if data.get("valid_until"):
                try:
                    valid_until = datetime.fromisoformat(data["valid_until"])
                    # Skip deals that have already expired
                    if valid_until.date() < now.date():
                        logger.info("[%s] Skipping expired deal: %s (expired %s)", self.source_name, data.get("title", ""), valid_until.date())
                        return None
                except ValueError:
                    pass

            deal_cat_str = data.get("deal_category", "restaurant")
            try:
                deal_category = DealCategory(deal_cat_str)
            except ValueError:
                deal_category = DealCategory.RESTAURANT

            return RawEvent(
                title=data.get("title", article["title"])[:120],
                source_url=article["url"],
                source_name=self.source_name,
                start_at=valid_from,
                end_at=valid_until,
                description=data.get("description", ""),
                is_free=bool(data.get("is_free", False)),
                event_type=EventType.DEAL,
                deal_category=deal_category,
                brand=data.get("brand", ""),
                discount_description=data.get("discount_description", ""),
                is_recurring=bool(data.get("is_recurring", False)),
                tags=data.get("tags", ["deal", "food"]),
            )

        except Exception as exc:
            logger.debug("Deal extraction failed for %s: %s", article["url"], exc)
            return None
