"""Tests for platform-specific copy generation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from copy_builder import build_copy, image_url_for_platform
from buffer_client import Platform

SITE_BASE = "https://novakidlife.com"

# ── Fixtures ───────────────────────────────────────────────────────────────────

def make_event(**overrides) -> dict:
    base = {
        "id":               "abc-123",
        "slug":             "storytime-fairfax-library-march-21",
        "title":            "Saturday Storytime at Fairfax Library",
        "description":      "Free drop-in storytime for children ages 2–6.",
        "start_at":         "2026-03-21T10:00:00-04:00",
        "end_at":           "2026-03-21T11:00:00-04:00",
        "location_name":    "Fairfax County Library — Chantilly",
        "location_address": "4100 Stringfellow Rd, Chantilly, VA 20151",
        "event_type":       "event",
        "section":          "main",
        "tags":             ["storytime", "kids", "library"],
        "is_free":          True,
        "cost_description": None,
        "image_url":        "https://media.novakidlife.com/events/storytime/hero.webp",
        "og_image_url":     "https://media.novakidlife.com/events/storytime/og.webp",
        "social_image_url": "https://media.novakidlife.com/events/storytime/social.webp",
    }
    base.update(overrides)
    return base


def make_pokemon_event(**overrides) -> dict:
    base = make_event(
        slug        = "pokemon-league-nerd-rage-manassas",
        title       = "Pokémon TCG League Night at Nerd Rage Gaming",
        description = "Weekly Pokémon TCG league night in Manassas.",
        location_name = "Nerd Rage Gaming",
        location_address = "7811 Sudley Rd, Manassas, VA 20109",
        event_type  = "pokemon_tcg",
        section     = "pokemon",
        tags        = ["pokémon tcg", "league", "competitive"],
        is_free     = False,
        cost_description = "$5 entry",
    )
    base.update(overrides)
    return base


# ── Twitter tests ──────────────────────────────────────────────────────────────

class TestTwitterCopy:
    def test_under_char_limit(self):
        copy = build_copy(make_event(), Platform.TWITTER)
        # Real URL replaced by 23-char t.co link
        url = f"{SITE_BASE}/events/storytime-fairfax-library-march-21"
        effective_len = len(copy.replace(url, "x" * 23))
        assert effective_len <= 280

    def test_contains_event_url(self):
        event = make_event()
        copy  = build_copy(event, Platform.TWITTER)
        assert f"{SITE_BASE}/events/{event['slug']}" in copy

    def test_contains_date(self):
        copy = build_copy(make_event(), Platform.TWITTER)
        assert "Mar" in copy or "March" in copy

    def test_contains_location(self):
        copy = build_copy(make_event(), Platform.TWITTER)
        assert "Fairfax" in copy or "Chantilly" in copy

    def test_has_hashtags(self):
        copy = build_copy(make_event(), Platform.TWITTER)
        assert "#NoVaKids" in copy

    def test_free_event_indicated(self):
        copy = build_copy(make_event(is_free=True), Platform.TWITTER)
        assert "Free" in copy or "free" in copy

    def test_pokemon_event_uses_pokemon_hashtags(self):
        copy = build_copy(make_pokemon_event(), Platform.TWITTER)
        assert "#PokemonTCG" in copy

    def test_pokemon_url_uses_pokemon_path(self):
        event = make_pokemon_event()
        copy  = build_copy(event, Platform.TWITTER)
        assert f"/pokemon/events/{event['slug']}" in copy

    def test_deal_event_copy(self):
        event = make_event(
            event_type="deal",
            title="BOGO Kids Meal at Chipotle",
            is_free=False,
            cost_description="Buy one kids meal, get one free",
        )
        copy = build_copy(event, Platform.TWITTER)
        assert "DEAL" in copy or "deal" in copy.lower()


# ── Instagram tests ────────────────────────────────────────────────────────────

class TestInstagramCopy:
    def test_contains_hashtag_block(self):
        copy = build_copy(make_event(), Platform.INSTAGRAM)
        assert copy.count("#") >= 8

    def test_contains_core_hashtags(self):
        copy = build_copy(make_event(), Platform.INSTAGRAM)
        assert "#NoVaKids" in copy
        assert "#FamilyFun" in copy

    def test_free_event_gets_free_hashtag(self):
        copy = build_copy(make_event(is_free=True), Platform.INSTAGRAM)
        assert "#FreeKidsEvents" in copy

    def test_contains_link_in_bio_cta(self):
        copy = build_copy(make_event(), Platform.INSTAGRAM)
        assert "Link in bio" in copy or "link in bio" in copy.lower()

    def test_contains_date_and_time(self):
        copy = build_copy(make_event(), Platform.INSTAGRAM)
        assert "📅" in copy
        assert "⏰" in copy

    def test_pokemon_gets_pokemon_hashtags(self):
        copy = build_copy(make_pokemon_event(), Platform.INSTAGRAM)
        assert "#PokemonTCG" in copy


# ── Facebook tests ─────────────────────────────────────────────────────────────

class TestFacebookCopy:
    def test_contains_full_address(self):
        copy = build_copy(make_event(), Platform.FACEBOOK)
        assert "Chantilly" in copy or "Stringfellow" in copy

    def test_contains_event_url(self):
        event = make_event()
        copy  = build_copy(event, Platform.FACEBOOK)
        assert f"{SITE_BASE}/events/{event['slug']}" in copy

    def test_contains_date_and_time(self):
        copy = build_copy(make_event(), Platform.FACEBOOK)
        assert "📅" in copy
        assert "⏰" in copy

    def test_free_indicator(self):
        copy = build_copy(make_event(is_free=True), Platform.FACEBOOK)
        assert "Free" in copy

    def test_low_hashtag_count(self):
        copy = build_copy(make_event(), Platform.FACEBOOK)
        # Facebook copy should use fewer hashtags than Instagram
        assert copy.count("#") <= 4


# ── Image URL selection ────────────────────────────────────────────────────────

class TestImageUrlForPlatform:
    def test_instagram_gets_square_image(self):
        event = make_event()
        url   = image_url_for_platform(event, Platform.INSTAGRAM)
        assert url == event["social_image_url"]

    def test_twitter_gets_og_image(self):
        event = make_event()
        url   = image_url_for_platform(event, Platform.TWITTER)
        assert url == event["og_image_url"]

    def test_facebook_gets_og_image(self):
        event = make_event()
        url   = image_url_for_platform(event, Platform.FACEBOOK)
        assert url == event["og_image_url"]

    def test_falls_back_to_image_url_if_og_missing(self):
        event = make_event(og_image_url=None)
        url   = image_url_for_platform(event, Platform.TWITTER)
        assert url == event["image_url"]

    def test_falls_back_to_image_url_if_social_missing(self):
        event = make_event(social_image_url=None)
        url   = image_url_for_platform(event, Platform.INSTAGRAM)
        assert url == event["image_url"]
