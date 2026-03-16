"""
Image processing pipeline — resize, convert to WebP, generate LQIP + blurhash.

Outputs a ProcessedImages bundle with all size variants ready for upload.

Variant spec:
  hero      1200×675   16:9   < 150 KB   website primary
  hero_md    800×450   16:9   <  80 KB   srcset medium
  hero_sm    400×225   16:9   <  35 KB   srcset small
  card       600×400   3:2    <  60 KB   event card thumbnail
  lqip        20×11   16:9   <   1 KB   base64 data URL for blur-up
  social    1080×1080   1:1   < 250 KB   social media post
  og        1200×630   ~16:9 < 200 KB   OpenGraph / Twitter card
"""
from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field

from PIL import Image


# ── Variant definitions ────────────────────────────────────────────────────────

@dataclass
class ImageVariant:
    key: str
    width: int
    height: int
    quality: int = 82        # WebP quality
    max_kb: int = 150        # soft size target (logged if exceeded)


WEBSITE_VARIANTS: list[ImageVariant] = [
    ImageVariant("hero",    1200, 675,  quality=85, max_kb=150),
    ImageVariant("hero_md",  800, 450,  quality=82, max_kb=80),
    ImageVariant("hero_sm",  400, 225,  quality=80, max_kb=35),
    ImageVariant("card",     600, 400,  quality=82, max_kb=60),
]

SOCIAL_VARIANT = ImageVariant("social", 1080, 1080, quality=85, max_kb=250)
OG_VARIANT     = ImageVariant("og",     1200,  630, quality=85, max_kb=200)

LQIP_WIDTH  = 20
LQIP_HEIGHT = 11


# ── Output bundle ──────────────────────────────────────────────────────────────

@dataclass
class ProcessedImages:
    """All image variants for one event, ready for S3 upload."""

    # Website variants (bytes)
    hero:    bytes = field(default=b"")
    hero_md: bytes = field(default=b"")
    hero_sm: bytes = field(default=b"")
    card:    bytes = field(default=b"")

    # Social / OG variants
    social: bytes = field(default=b"")
    og:     bytes = field(default=b"")

    # LQIP — tiny placeholder encoded as a base64 WebP data URL
    lqip_data_url: str = field(default="")

    # Blurhash — compact visual hash for CSS blur-up (stored in DB)
    blurhash: str = field(default="")

    # Dimensions (always fixed per variant — stored in DB to prevent CLS)
    image_width:  int = 1200
    image_height: int = 675


# ── Helpers ────────────────────────────────────────────────────────────────────

def _smart_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """
    Resize + center-crop to exact target dimensions.
    Preserves aspect ratio before cropping so no distortion.
    """
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio    = src_w  / src_h

    if src_ratio > target_ratio:
        # Source is wider — scale by height, then crop width
        new_h = target_h
        new_w = int(src_w * (target_h / src_h))
    else:
        # Source is taller — scale by width, then crop height
        new_w = target_w
        new_h = int(src_h * (target_w / src_w))

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - target_w) // 2
    top  = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _to_webp(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    return buf.getvalue()


def _make_lqip(img: Image.Image) -> str:
    """Return a base64 WebP data URL for a 20×11 thumbnail."""
    tiny = img.resize((LQIP_WIDTH, LQIP_HEIGHT), Image.LANCZOS)
    buf = io.BytesIO()
    tiny.save(buf, format="WEBP", quality=30)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/webp;base64,{b64}"


def _make_blurhash(img: Image.Image) -> str:
    """Generate blurhash for CSS blur-up placeholder."""
    try:
        import blurhash
        # Blurhash needs small image for speed
        small = img.resize((64, 36), Image.LANCZOS)
        return blurhash.encode(small, x_components=4, y_components=3)
    except Exception:
        return ""


# ── Public API ─────────────────────────────────────────────────────────────────

def process_website_image(image_bytes: bytes) -> ProcessedImages:
    """
    Process a sourced/generated image into all website + OG variants.

    Input image should already have warm grade applied (from enhancer.py).

    Args:
        image_bytes: JPEG bytes from enhancer.apply_warm_grade()

    Returns:
        ProcessedImages with all variants populated
    """
    src = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    result = ProcessedImages()

    # Website variants
    for variant in WEBSITE_VARIANTS:
        cropped = _smart_crop(src, variant.width, variant.height)
        webp    = _to_webp(cropped, variant.quality)
        setattr(result, variant.key, webp)

    # OG variant
    og_img = _smart_crop(src, OG_VARIANT.width, OG_VARIANT.height)
    result.og = _to_webp(og_img, OG_VARIANT.quality)

    # LQIP from hero dimensions
    hero_img = _smart_crop(src, 1200, 675)
    result.lqip_data_url = _make_lqip(hero_img)
    result.blurhash      = _make_blurhash(hero_img)

    return result


def process_social_image(image_bytes: bytes) -> bytes:
    """
    Process a social illustration into the 1080×1080 WebP variant.

    Args:
        image_bytes: Raw image bytes from generator.generate_image()

    Returns:
        WebP bytes for the social variant
    """
    src     = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    cropped = _smart_crop(src, SOCIAL_VARIANT.width, SOCIAL_VARIANT.height)
    return _to_webp(cropped, SOCIAL_VARIANT.quality)
