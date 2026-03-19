# Skill: Generate Event Images — SOP

**Purpose:** Run the image generation pipeline for one or more events.
Produces all WebP variants, LQIP placeholder, blurhash, SEO alt text, and uploads to S3.

**Service:** `services/image-gen/`

> For sourcing logic, prompt libraries, and venue Place IDs — see `generate-image-source.md`.

---

## Pipeline Overview

```
Event dict (id, slug, title, tags, section, ...)
    │
    ├── sourcer.py       scraped image_url → Google Places → Unsplash → Pexels → None (AI fallback)
    │
    ├── generator.py     Imagen 3 (Vertex AI) → DALL-E 3 fallback (only if sourcer returns None)
    │
    ├── enhancer.py      Pillow warm color grade
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
| Google Places Photos | ~$0.017/call | Venue photo lookup |

Sourced images (scraped URL, Unsplash, Pexels): **$0** — skips all AI calls.
Estimated blended cost with ~60% sourced: **~$0.02/event**
