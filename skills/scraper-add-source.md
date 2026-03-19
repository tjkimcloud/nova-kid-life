---
name: scraper-add-source
description: How to add a new event source to the NovaKidLife scraper — Tier 2 config-driven (zero code), Tier 1 structured scraper, and Pokémon LGS entries. Also contains the RawEvent model reference and the full source registry counts.
triggers:
  - add source
  - new scraper
  - sources.json
  - Tier 2
  - Tier 1
  - LGS
  - RawEvent
  - scraper architecture
---

# Skill: Add a Scraper Source

**Service:** `services/events-scraper/`

---

## Adding a New Tier 2 Source — Zero Code Required

Tier 2 is config-driven. Add one entry to `services/events-scraper/config/sources.json`:

```json
{
  "name": "my-new-source",
  "url": "https://example.com/events/",
  "enabled": true,
  "schedule": "daily",
  "description": "Brief description of what this source covers",
  "tags": ["community", "nova"]
}
```

The AI extractor (`scrapers/tier2/ai_extractor.py`) picks it up automatically on next deploy.
No code changes needed. Deploy with `python scripts/deploy-lambdas.py events-scraper`.

---

## Adding a New Tier 1 Source — Structured Scraper

Use for high-value official sources with known APIs (libraries, parks depts, Eventbrite).

1. Create `services/events-scraper/scrapers/tier1/my_scraper.py`
2. Extend `BaseScraper`, implement `scrape() -> list[RawEvent]`
3. Add the class reference to `config/sources.json` under `tier1_events`

---

## Adding a Pokémon LGS

Add an entry to `_NOVA_LGS` list in `scrapers/pokemon/events_scraper.py`:

```python
{
    "name":     "Store Name",
    "url":      "https://storename.com/events",
    "location": "City, VA",
    "zip":      "20XXX",
}
```

---

## RawEvent Model Reference

All scrapers return `list[RawEvent]`. Key fields:

```python
@dataclass
class RawEvent:
    title:         str
    source_url:    str
    source_name:   str
    start_at:      datetime | None
    event_type:    EventType   # event | deal | birthday_freebie | amusement |
                               # seasonal | pokemon_tcg | product_drop
    section:       str         # 'main' | 'pokemon'
    slug:          str         # URL-safe identifier
    description:   str
    location_name: str
    tags:          list[str]
    brand:         str         # for deals/drops (e.g. "The Pokémon Company")
    image_url:     str         # if scraped source has one
```

---

## Source Registry (from `config/sources.json`)

| Key | Count | Schedule |
|-----|-------|----------|
| `tier1_events` | 4 | Daily |
| `tier2_events` | 12 | Daily |
| `tier3_deals` | 5 | 4×/day or daily |
| `pokemon_events` | 3 | Daily or weekly |

---

## Architecture Overview

```
EventBridge (daily 6am EST)
    │
    ▼
events-scraper Lambda (handler.py)
    │
    ├── Tier 1 — Structured scrapers (4 sources)
    │     LibCal API → JSON-LD → AI fallback
    │
    ├── Tier 2 — AI-extracted sources (12 sources, config-driven)
    │     URL → clean HTML → gpt-4o-mini → RawEvent[]
    │     ** Add new source: 1 JSON entry in config/sources.json — zero code **
    │
    ├── Tier 3 — Deal monitors (5 sources)
    │     KrazyCouponLady, Hip2Save, Google News RSS
    │
    └── Pokémon TCG section (3 sources)
          Play! Pokémon locator + 5 LGS + Google News
    │
    ▼
SQS Queue: novakidlife-events-queue
    │
    └── image-gen Lambda → Supabase events table
```

## Deduplication

Events are deduplicated in Supabase using a unique constraint on `source_url`.
The publisher does `INSERT ... ON CONFLICT (source_url) DO UPDATE SET updated_at = now()`.
Re-running the same scraper is safe — no duplicate rows are created.
