# Skill: Generate Event Images

**Purpose:** Run the image generation pipeline for one or more events.
Produces all WebP variants, LQIP placeholder, blurhash, SEO alt text, and uploads to S3.

## Service: `services/image-gen/`

---

## Pipeline Overview

```
Event dict (id, slug, title, tags, section, ...)
    │
    ├── sourcer.py       scraped image_url → Google Places Photos → None
    │
    ├── generator.py     (only if sourcer returns None)
    │                    Imagen 3 (Vertex AI) → DALL-E 3 fallback
    │
    ├── enhancer.py      Pillow warm color grade on all images
    │                    warmth shift (R×1.05, B×0.90), contrast, saturation, vignette
    │
    ├── processor.py     Resize + WebP encode all variants:
    │                      hero      1200×675   16:9   website primary
    │                      hero-md    800×450   16:9   srcset medium
    │                      hero-sm    400×225   16:9   srcset small
    │                      card       600×400   3:2    event card
    │                      og        1200×630   ~16:9  OpenGraph
    │                      lqip        20×11    16:9   base64 data URL (blur-up)
    │                      blurhash   4×3 components   CSS placeholder
    │
    ├── generator.py     Social image (always AI — never sourced)
    │                    1080×1080 flat editorial illustration
    │
    ├── alt_text.py      gpt-4o-mini → ≤125 char SEO alt text
    │
    ├── uploader.py      S3: events/{slug}/*.webp
    │                    Cache-Control: public, max-age=31536000, immutable
    │
    └── Supabase PATCH   Updates 10 image columns on events row
```

---

## Prompt Libraries (`prompts.py`)

### Website (photorealistic editorial photography)
`WEBSITE_PROMPTS` — 14 keys:
`library`, `outdoor`, `arts-crafts`, `sports`, `educational`, `music`, `nature`,
`holiday`, `swimming`, `theater`, `food`, `deal_restaurant`, `deal_birthday`,
`deal_amusement`, `default`

Style constant: `"Professional editorial photography, warm golden hour lighting, amber and sage color tones, sharp focus, Northern Virginia suburban setting"`

### Social (flat editorial illustration)
`SOCIAL_PROMPTS` — same 14 keys

Style constant: `"Flat editorial illustration, warm amber and sage green color palette, rounded friendly shapes, clean vector art style, families and children, joyful community atmosphere"`

### Pokémon TCG (`section = 'pokemon'`)
`POKEMON_PROMPTS` — 7 keys:
`league`, `prerelease`, `regional`, `product_drop`, `product_drop_social`,
`league_social`, `default`

Events with `section = 'pokemon'` automatically route to `POKEMON_PROMPTS`.

### Prompt selection
```python
from prompts import get_website_prompt, get_social_prompt, get_pokemon_prompt

# Standard events
website_prompt = get_website_prompt(event)   # tag-based matching
social_prompt  = get_social_prompt(event)

# Pokémon events
website_prompt = get_pokemon_prompt(event, style="website")
social_prompt  = get_pokemon_prompt(event, style="social")
```

---

## Image Sourcing (`sourcer.py`)

Priority order:
1. `event["image_url"]` — if present and looks like a real image (not placeholder/icon)
2. Google Places Photos API — for known NoVa venues (pre-seeded Place IDs)
3. `None` → AI generation

Pre-seeded Place IDs cover: Fairfax County Library, George Mason University, Reston Town Center, Wolf Trap, Burke Lake Park, Meadowlark Botanical Gardens, Claude Moore Colonial Farm, Sully Historic Site.

Requires: `GOOGLE_PLACES_API_KEY` env var (optional — falls back gracefully without it)

---

## S3 Upload Paths

```
events/{event-slug}/hero.webp        1200×675   < 150 KB
events/{event-slug}/hero-md.webp      800×450   <  80 KB
events/{event-slug}/hero-sm.webp      400×225   <  35 KB
events/{event-slug}/card.webp         600×400   <  60 KB
events/{event-slug}/og.webp          1200×630   < 200 KB
events/{event-slug}/social.webp     1080×1080   < 250 KB
```

CDN base URL: `https://media.novakidlife.com`

---

## Manual Invocation (local test)

```python
# From services/image-gen/
import json
from handler import process_event

event = {
    "id":            "test-123",
    "slug":          "fairfax-storytime-2026-03-20",
    "title":         "Storytime at Fairfax County Library",
    "location_name": "Fairfax County Library",
    "event_type":    "event",
    "section":       "main",
    "tags":          ["library", "storytime", "kids"],
    "description":   "Join us for a fun storytime session for kids ages 2-6.",
}

result = process_event(event)
print(result)
# {"status": "ok", "slug": "fairfax-storytime-2026-03-20", "hero_url": "https://media.novakidlife.com/..."}
```

---

## Lambda Trigger (SQS)

```json
{
  "Records": [
    {
      "body": "{\"id\": \"abc123\", \"slug\": \"event-slug\", \"title\": \"...\", \"section\": \"main\", ...}"
    }
  ]
}
```

---

## Running Tests

```bash
cd services/image-gen
pip install -r requirements.txt
pytest tests/test_processor.py -v
```

14 tests covering: all size variants, WebP format, LQIP data URL correctness, file size limits, portrait-to-landscape crop.

---

## Cost Estimate

| Provider | Cost | When used |
|----------|------|-----------|
| Imagen 3 | ~$0.04/image | Primary — all AI-generated images |
| DALL-E 3 HD | ~$0.08/image | Fallback — only if Imagen 3 fails |
| gpt-4o-mini | ~$0.001/call | Alt text generation |
| Google Places Photos | ~$0.017/call | Venue photo lookup (skipped if pre-seeded) |

Sourced images (from scraped URL): **$0** — skips all AI calls.
Estimated blended cost with ~60% sourced: **~$0.02/event**
