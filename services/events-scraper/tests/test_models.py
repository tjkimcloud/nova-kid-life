"""Tests for RawEvent model."""
from datetime import datetime, timezone

import pytest

from scrapers.models import DealCategory, EventType, RawEvent


def make_event(**kwargs) -> RawEvent:
    defaults = {
        "title": "Test Event",
        "source_url": "https://example.com/event/1",
        "source_name": "test-source",
        "start_at": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
    }
    return RawEvent(**{**defaults, **kwargs})


def test_default_event_type():
    event = make_event()
    assert event.event_type == EventType.EVENT
    assert not event.is_deal


def test_deal_event_type():
    deal = make_event(event_type=EventType.DEAL, brand="Chipotle")
    assert deal.is_deal
    assert deal.brand == "Chipotle"


def test_to_dict_serializable():
    event = make_event()
    d = event.to_dict()
    import json
    assert json.dumps(d)  # Must be JSON-serializable
    assert d["title"] == "Test Event"
    assert d["event_type"] == "event"


def test_to_dict_deal():
    deal = make_event(
        event_type=EventType.DEAL,
        deal_category=DealCategory.RESTAURANT,
        brand="Shake Shack",
        discount_description="Free ShackBurger with app download",
    )
    d = deal.to_dict()
    assert d["event_type"] == "deal"
    assert d["deal_category"] == "restaurant"
    assert d["brand"] == "Shake Shack"


def test_source_url_stripped():
    event = make_event(source_url="  https://example.com/event  ")
    assert event.source_url == "https://example.com/event"


def test_tags_default_empty():
    event = make_event()
    assert event.tags == []


def test_birthday_freebie():
    freebie = make_event(
        event_type=EventType.BIRTHDAY_FREEBIE,
        is_recurring=True,
        brand="Dairy Queen",
        discount_description="Free Blizzard on your birthday",
    )
    assert freebie.is_deal
    assert freebie.is_recurring
