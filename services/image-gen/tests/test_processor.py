"""
Tests for the image processor pipeline.

Uses a generated test image (no external API calls required).
"""
import io
import sys
import os

import pytest
from PIL import Image

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from processor import (
    process_website_image,
    process_social_image,
    ProcessedImages,
    LQIP_WIDTH,
    LQIP_HEIGHT,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _make_jpeg(width: int = 1920, height: int = 1080) -> bytes:
    """Create a test JPEG image filled with amber color."""
    img = Image.new("RGB", (width, height), color=(245, 158, 11))  # amber-500
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


def _make_square_jpeg(size: int = 1024) -> bytes:
    """Create a test square JPEG."""
    img = Image.new("RGB", (size, size), color=(100, 150, 100))  # sage-ish
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return buf.getvalue()


# ── Website processing tests ───────────────────────────────────────────────────

class TestProcessWebsiteImage:
    def setup_method(self):
        self.jpeg = _make_jpeg()
        self.result: ProcessedImages = process_website_image(self.jpeg)

    def test_returns_processed_images(self):
        assert isinstance(self.result, ProcessedImages)

    def test_hero_is_1200x675(self):
        img = Image.open(io.BytesIO(self.result.hero))
        assert img.size == (1200, 675)

    def test_hero_md_is_800x450(self):
        img = Image.open(io.BytesIO(self.result.hero_md))
        assert img.size == (800, 450)

    def test_hero_sm_is_400x225(self):
        img = Image.open(io.BytesIO(self.result.hero_sm))
        assert img.size == (400, 225)

    def test_card_is_600x400(self):
        img = Image.open(io.BytesIO(self.result.card))
        assert img.size == (600, 400)

    def test_og_is_1200x630(self):
        img = Image.open(io.BytesIO(self.result.og))
        assert img.size == (1200, 630)

    def test_hero_is_webp(self):
        img = Image.open(io.BytesIO(self.result.hero))
        assert img.format == "WEBP"

    def test_hero_under_150kb(self):
        assert len(self.result.hero) < 150 * 1024

    def test_hero_sm_under_35kb(self):
        assert len(self.result.hero_sm) < 35 * 1024

    def test_lqip_is_data_url(self):
        assert self.result.lqip_data_url.startswith("data:image/webp;base64,")

    def test_lqip_decodes_to_correct_size(self):
        import base64
        data = self.result.lqip_data_url.split(",", 1)[1]
        raw = base64.b64decode(data)
        img = Image.open(io.BytesIO(raw))
        assert img.size == (LQIP_WIDTH, LQIP_HEIGHT)

    def test_dimensions_set(self):
        assert self.result.image_width  == 1200
        assert self.result.image_height == 675


class TestProcessWebsiteImagePortraitSource:
    """Ensure portrait-orientation source images are handled correctly."""

    def test_portrait_source_crops_to_landscape(self):
        portrait_jpeg = _make_jpeg(width=800, height=1200)
        result = process_website_image(portrait_jpeg)
        img = Image.open(io.BytesIO(result.hero))
        assert img.size == (1200, 675)


# ── Social processing tests ────────────────────────────────────────────────────

class TestProcessSocialImage:
    def test_square_input_to_1080x1080(self):
        raw = _make_square_jpeg()
        webp = process_social_image(raw)
        img = Image.open(io.BytesIO(webp))
        assert img.size == (1080, 1080)

    def test_landscape_input_to_1080x1080(self):
        raw = _make_jpeg(1920, 1080)
        webp = process_social_image(raw)
        img = Image.open(io.BytesIO(webp))
        assert img.size == (1080, 1080)

    def test_social_is_webp(self):
        raw = _make_square_jpeg()
        webp = process_social_image(raw)
        img = Image.open(io.BytesIO(webp))
        assert img.format == "WEBP"

    def test_social_under_250kb(self):
        raw = _make_square_jpeg(2048)
        webp = process_social_image(raw)
        assert len(webp) < 250 * 1024
