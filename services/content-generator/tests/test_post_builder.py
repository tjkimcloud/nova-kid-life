"""
Unit tests for content-generator post_builder module.
No external dependencies — all Supabase/OpenAI calls are mocked.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from post_builder import (
    AREAS,
    PostSpec,
    _build_specs,
    _make_slug,
    _select_prompt,
    get_upcoming_weekend,
    get_upcoming_week,
    post_exists,
)


# ── Date helpers ───────────────────────────────────────────────────────────────

class TestGetUpcomingWeekend:
    def test_returns_friday_and_sunday(self):
        # Wednesday → next Friday
        wednesday = date(2026, 3, 18)
        friday, sunday = get_upcoming_weekend(wednesday)
        assert friday.weekday() == 4   # Friday
        assert sunday.weekday() == 6   # Sunday
        assert (sunday - friday).days == 2

    def test_from_friday_gives_next_friday(self):
        # Friday should return NEXT Friday, not today
        friday = date(2026, 3, 20)
        next_fri, _ = get_upcoming_weekend(friday)
        assert next_fri > friday

    def test_from_saturday_gives_next_friday(self):
        saturday = date(2026, 3, 21)
        friday, _ = get_upcoming_weekend(saturday)
        assert friday.weekday() == 4
        assert friday > saturday


class TestGetUpcomingWeek:
    def test_returns_monday_and_sunday(self):
        wednesday = date(2026, 3, 18)
        monday, sunday = get_upcoming_week(wednesday)
        assert monday.weekday() == 0   # Monday
        assert sunday.weekday() == 6   # Sunday
        assert (sunday - monday).days == 6


# ── Slug generation ────────────────────────────────────────────────────────────

class TestMakeSlug:
    def test_weekend_roundup_slug(self):
        spec = PostSpec(
            post_type="weekend_roundup",
            area="nova",
            date_range_start=date(2026, 3, 20),
            date_range_end=date(2026, 3, 22),
            area_label="Northern Virginia",
            county_label="NoVa",
            location_names=None,
        )
        slug = _make_slug(spec)
        assert "northern-virginia" in slug
        assert "weekend" in slug
        assert " " not in slug
        assert slug == slug.lower()

    def test_location_specific_slug(self):
        spec = PostSpec(
            post_type="location_specific",
            area="fairfax",
            date_range_start=date(2026, 3, 20),
            date_range_end=date(2026, 3, 22),
            area_label="Fairfax County",
            county_label="Fairfax County",
            location_names=["Fairfax"],
        )
        slug = _make_slug(spec)
        assert "fairfax" in slug
        assert " " not in slug

    def test_free_events_slug(self):
        spec = PostSpec(
            post_type="free_events",
            area="nova",
            date_range_start=date(2026, 3, 20),
            date_range_end=date(2026, 3, 22),
            area_label="Northern Virginia",
            county_label="NoVa",
            location_names=None,
        )
        slug = _make_slug(spec)
        assert "free" in slug

    def test_no_double_hyphens(self):
        spec = PostSpec(
            post_type="indoor",
            area="nova",
            date_range_start=date(2026, 3, 20),
            date_range_end=date(2026, 3, 22),
            area_label="Northern Virginia",
            county_label="NoVa",
            location_names=None,
        )
        slug = _make_slug(spec)
        assert "--" not in slug


# ── Spec builder ───────────────────────────────────────────────────────────────

class TestBuildSpecs:
    def test_weekend_generates_expected_types(self):
        start = date(2026, 3, 20)
        end   = date(2026, 3, 22)
        specs = _build_specs("weekend", start, end)
        post_types = [s.post_type for s in specs]
        assert "weekend_roundup"    in post_types
        assert "location_specific"  in post_types
        assert "free_events"        in post_types
        assert "indoor"             in post_types

    def test_weekend_includes_major_areas(self):
        start = date(2026, 3, 20)
        end   = date(2026, 3, 22)
        specs = _build_specs("weekend", start, end)
        areas = [s.area for s in specs if s.post_type == "location_specific"]
        assert "fairfax"    in areas
        assert "loudoun"    in areas
        assert "arlington"  in areas
        assert "alexandria" in areas

    def test_week_ahead_generates_single_spec(self):
        start = date(2026, 3, 23)
        end   = date(2026, 3, 29)
        specs = _build_specs("week_ahead", start, end)
        assert len(specs) == 1
        assert specs[0].post_type == "week_ahead"


# ── post_exists ────────────────────────────────────────────────────────────────

class TestPostExists:
    def test_returns_true_when_post_found(self):
        db = MagicMock()
        db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = [{"id": "abc"}]
        assert post_exists(db, "weekend_roundup", "nova", date(2026, 3, 20)) is True

    def test_returns_false_when_no_post(self):
        db = MagicMock()
        db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        assert post_exists(db, "weekend_roundup", "nova", date(2026, 3, 20)) is False


# ── Prompt selection ───────────────────────────────────────────────────────────

class TestSelectPrompt:
    def _make_spec(self, post_type: str) -> PostSpec:
        return PostSpec(
            post_type=post_type,
            area="nova",
            date_range_start=date(2026, 3, 20),
            date_range_end=date(2026, 3, 22),
            area_label="Northern Virginia",
            county_label="NoVa",
            location_names=None,
        )

    def _sample_events(self) -> list[dict]:
        return [
            {
                "id": "1", "slug": "test-event", "title": "Test Event",
                "short_description": "A test event.", "start_at": "2026-03-21T10:00:00",
                "venue_name": "Test Venue", "location_text": "Fairfax, VA",
                "is_free": True, "cost_description": None, "tags": ["family"],
            }
        ]

    @pytest.mark.parametrize("post_type", [
        "weekend_roundup", "location_specific", "free_events", "week_ahead", "indoor"
    ])
    def test_prompt_is_nonempty_string(self, post_type: str):
        spec   = self._make_spec(post_type)
        events = self._sample_events()
        prompt = _select_prompt(spec, events, date(2026, 3, 20), date(2026, 3, 22))
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_prompt_contains_area_label(self):
        spec   = self._make_spec("weekend_roundup")
        events = self._sample_events()
        prompt = _select_prompt(spec, events, date(2026, 3, 20), date(2026, 3, 22))
        assert "Northern Virginia" in prompt

    def test_unknown_post_type_raises(self):
        spec = self._make_spec("invalid_type")
        with pytest.raises(ValueError):
            _select_prompt(spec, [], date(2026, 3, 20), date(2026, 3, 22))
