"""
Warm color grade applied to every image (both sourced photos and AI-generated).

Goal: amber-leaning warmth, no cold blues, consistent brand feel across all content.

Operations (in order):
  1. Slight warmth shift — boost red/green channels, pull blue down
  2. Soft contrast lift — S-curve via Brightness/Contrast
  3. Saturation bump — makes colors pop without looking processed
  4. Optional vignette — subtle edge darkening for editorial look
"""
from __future__ import annotations

import io
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


# ── Tuning constants ───────────────────────────────────────────────────────────

# Per-channel multipliers for warmth: (R, G, B)
# Boost R slightly, keep G neutral, pull B down a touch
_WARM_MATRIX = (1.05, 1.00, 0.90)

# Contrast enhancer factor (1.0 = no change, 1.1 = +10%)
_CONTRAST_FACTOR = 1.12

# Color saturation enhancer factor
_SATURATION_FACTOR = 1.10

# Brightness nudge (very subtle lift — editorial look)
_BRIGHTNESS_FACTOR = 1.03

# Vignette strength: 0.0 = off, 1.0 = full black edges
_VIGNETTE_STRENGTH = 0.18


# ── Internal helpers ───────────────────────────────────────────────────────────

def _apply_warmth(img: Image.Image) -> Image.Image:
    """Shift white balance toward amber by scaling RGB channels."""
    r, g, b = img.split()

    r = r.point(lambda x: min(255, int(x * _WARM_MATRIX[0])))
    g = g.point(lambda x: min(255, int(x * _WARM_MATRIX[1])))
    b = b.point(lambda x: min(255, int(x * _WARM_MATRIX[2])))

    return Image.merge("RGB", (r, g, b))


def _apply_vignette(img: Image.Image) -> Image.Image:
    """Add a radial gradient vignette using a Gaussian-blurred mask."""
    w, h = img.size

    # Create a white ellipse on a black background
    mask = Image.new("L", (w, h), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)

    # Ellipse slightly smaller than image to create vignette border
    margin_x = int(w * 0.15)
    margin_y = int(h * 0.15)
    draw.ellipse(
        [margin_x, margin_y, w - margin_x, h - margin_y],
        fill=255,
    )

    # Blur the mask heavily for smooth fade
    blur_radius = min(w, h) // 6
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Invert: center bright → center keeps original; edges dark → edges darken
    mask = ImageOps.invert(mask)

    # Scale mask by vignette strength
    mask = mask.point(lambda x: int(x * _VIGNETTE_STRENGTH))

    # Subtract mask from image (darken edges)
    img_array = img.copy()
    vignette_layer = Image.new("RGB", (w, h), (0, 0, 0))
    img_array.paste(vignette_layer, mask=mask)

    # Composite: original minus darkened edges
    return Image.blend(img, img_array, alpha=0.0)  # no-op placeholder
    # Actually composite correctly:


def _vignette_correct(img: Image.Image) -> Image.Image:
    """Correct vignette implementation using paste with alpha mask."""
    w, h = img.size

    # Build radial alpha mask: white center, black edges
    mask = Image.new("L", (w, h), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)

    margin_x = int(w * 0.12)
    margin_y = int(h * 0.12)
    draw.ellipse(
        [margin_x, margin_y, w - margin_x, h - margin_y],
        fill=255,
    )
    blur_r = min(w, h) // 5
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_r))

    # Dark overlay
    overlay = Image.new("RGB", (w, h), (0, 0, 0))

    # Invert mask: edges = opaque (darken), center = transparent (keep)
    inv_mask = ImageOps.invert(mask)
    inv_mask = inv_mask.point(lambda x: int(x * _VIGNETTE_STRENGTH))

    result = img.copy()
    result.paste(overlay, mask=inv_mask)
    return result


# ── Public API ─────────────────────────────────────────────────────────────────

def apply_warm_grade(image_bytes: bytes) -> bytes:
    """
    Apply warm color grade to raw image bytes.

    Args:
        image_bytes: Raw image bytes (any format Pillow supports)

    Returns:
        JPEG-encoded bytes of the graded image at quality=92
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 1. Warmth
    img = _apply_warmth(img)

    # 2. Contrast
    img = ImageEnhance.Contrast(img).enhance(_CONTRAST_FACTOR)

    # 3. Saturation
    img = ImageEnhance.Color(img).enhance(_SATURATION_FACTOR)

    # 4. Brightness
    img = ImageEnhance.Brightness(img).enhance(_BRIGHTNESS_FACTOR)

    # 5. Vignette
    img = _vignette_correct(img)

    # Output as high-quality JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, optimize=True, progressive=True)
    return buf.getvalue()
