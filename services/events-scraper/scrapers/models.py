"""
Data models for raw scraped content before AI enrichment.
All scrapers return lists of RawEvent objects.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    EVENT            = "event"
    DEAL             = "deal"
    BIRTHDAY_FREEBIE = "birthday_freebie"
    AMUSEMENT        = "amusement"
    SEASONAL         = "seasonal"
    POKEMON_TCG      = "pokemon_tcg"   # Leagues, prereleases, tournaments
    PRODUCT_DROP     = "product_drop"  # New set releases with retailer matrix


class DealCategory(str, Enum):
    RESTAURANT = "restaurant"
    ACTIVITY   = "activity"
    AMUSEMENT  = "amusement"
    GROCERY    = "grocery"
    SEASONAL   = "seasonal"


@dataclass
class RawEvent:
    # ── Required ──────────────────────────────────────────────────────────────
    title:       str
    source_url:  str
    source_name: str
    start_at:    datetime

    # ── Event classification ───────────────────────────────────────────────────
    event_type:    EventType = EventType.EVENT
    deal_category: DealCategory | None = None

    # ── Timing ────────────────────────────────────────────────────────────────
    end_at:       datetime | None = None
    is_recurring: bool = False           # True for birthday freebies, annual events

    # ── Content ───────────────────────────────────────────────────────────────
    description:       str = ""
    registration_url:  str = ""
    image_url:         str = ""

    # ── Location (events) ─────────────────────────────────────────────────────
    location_text: str = ""
    venue_name:    str = ""
    address:       str = ""
    lat:           float | None = None
    lng:           float | None = None

    # ── Audience ──────────────────────────────────────────────────────────────
    age_range: str = ""
    tags:      list[str] = field(default_factory=list)

    # ── Cost ──────────────────────────────────────────────────────────────────
    is_free:          bool = False
    cost_description: str = ""

    # ── Site section routing ──────────────────────────────────────────────────
    section: str = "main"  # "main" | "pokemon" — maps to site URL section

    # ── Slug ──────────────────────────────────────────────────────────────────
    slug: str = ""

    # ── Deal-specific (populated when event_type != EVENT) ────────────────────
    brand:                str = ""   # "Chipotle", "Shake Shack", "Kings Dominion"
    discount_description: str = ""  # "BOGO entrée", "Free burger on your birthday"

    # ── Location aliases (pokemon scrapers use these field names) ─────────────
    location_name:    str = ""
    location_address: str = ""

    def __post_init__(self) -> None:
        # Ensure source_url is always stripped and lowercase-scheme
        self.source_url = self.source_url.strip()

    @property
    def is_deal(self) -> bool:
        return self.event_type != EventType.EVENT

    def to_dict(self) -> dict:
        """Serialize to a dict safe for JSON / SQS message body."""
        return {
            "title":                self.title,
            "source_url":           self.source_url,
            "source_name":          self.source_name,
            "start_at":             self.start_at.isoformat(),
            "end_at":               self.end_at.isoformat() if self.end_at else None,
            "event_type":           self.event_type.value,
            "deal_category":        self.deal_category.value if self.deal_category else None,
            "is_recurring":         self.is_recurring,
            "description":          self.description,
            "registration_url":     self.registration_url,
            "image_url":            self.image_url,
            "location_text":        self.location_text,
            "venue_name":           self.venue_name,
            "address":              self.address,
            "lat":                  self.lat,
            "lng":                  self.lng,
            "age_range":            self.age_range,
            "tags":                 self.tags,
            "is_free":              self.is_free,
            "cost_description":     self.cost_description,
            "brand":                self.brand,
            "discount_description": self.discount_description,
            "section":              self.section,
            "slug":                 self.slug,
        }
