# Skill: Scrape Events

**Purpose:** Trigger and monitor the events scraper Lambda.
Covers all tiers: structured library scrapers, AI-extracted sources, deal monitors, and the Pokémon TCG section.

## Service: `services/events-scraper/`

---

## Scraper Architecture

```
EventBridge (daily 6am EST)
    │
    ▼
events-scraper Lambda (handler.py)
    │
    ├── Tier 1 — Structured scrapers (4 sources)
    │     scrapers/tier1/fairfax_library.py    LibCal API → JSON-LD → AI fallback
    │     scrapers/tier1/loudoun_library.py    LibCal API → JSON-LD → AI fallback
    │     scrapers/tier1/arlington_library.py  LibCal API → JSON-LD → AI fallback
    │     scrapers/tier1/eventbrite_nova.py    JSON-LD across 5 NoVa city URLs
    │
    ├── Tier 2 — AI-extracted sources (12 sources, config-driven)
    │     scrapers/tier2/ai_extractor.py       URL → clean HTML → gpt-4o-mini → RawEvent[]
    │     Sources: dullesmoms, nova-moms-blog, patch.com (4 cities),
    │              things-to-do-dc, bring-the-kids, reston-association,
    │              fairfax-parks, loudoun-parks, nova-kids-activities
    │     ** Add a new source: 1 JSON entry in config/sources.json — zero code **
    │
    ├── Tier 3 — Deal monitors (5 sources)
    │     scrapers/tier3/krazy_coupon_lady.py  Restaurant + freebie deals
    │     scrapers/tier3/hip2save.py           Family + restaurant deals
    │     scrapers/tier3/google_news_rss.py    Viral deals via Google News RSS
    │     (+ birthday freebies + amusement deal queries via Google News)
    │
    └── Pokémon TCG section (3 sources, section='pokemon')
          scrapers/pokemon/events_scraper.py   Play! Pokémon locator (15 NoVa zips) + 5 LGS
          scrapers/pokemon/drops_scraper.py    Release calendar + NoVa retailer matrix
          google_news_rss.py                  Pokemon-specific Google News queries
    │
    ▼
SQS Queue: novakidlife-events-queue
    │
    ├── image-gen Lambda    → generates + uploads all image variants
    └── Supabase events table
```

---

## RawEvent Model

All scrapers return `list[RawEvent]`. Key fields:

```python
@dataclass
class RawEvent:
    title:        str
    source_url:   str
    source_name:  str
    start_at:     datetime | None

    event_type:   EventType   # event | deal | birthday_freebie | amusement |
                              # seasonal | pokemon_tcg | product_drop
    section:      str         # 'main' | 'pokemon'
    slug:         str         # URL-safe identifier

    description:  str
    location_name: str
    tags:         list[str]
    brand:        str         # for deals/drops (e.g. "The Pokémon Company")
    image_url:    str         # if scraped source has one
```

---

## Adding a New Source

### Tier 2 (AI-extracted) — zero code required
Add one entry to `services/events-scraper/config/sources.json`:
```json
{
  "name": "my-new-source",
  "url": "https://example.com/events/",
  "enabled": true,
  "schedule": "daily",
  "description": "Brief description",
  "tags": ["community", "nova"]
}
```

### Tier 1 (structured) — for high-value sources with known APIs
1. Create `services/events-scraper/scrapers/tier1/my_scraper.py`
2. Extend `BaseScraper`, implement `scrape() -> list[RawEvent]`
3. Add class reference to `config/sources.json` under `tier1_events`

### Pokémon LGS — add to events_scraper.py
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

## Manual Invocation

```bash
# Trigger full scrape (all sources)
aws lambda invoke \
  --function-name novakidlife-events-scraper \
  --payload '{"source": "manual", "targets": ["all"]}' \
  --log-type Tail \
  /tmp/scrape-response.json

# Scrape specific source only
aws lambda invoke \
  --function-name novakidlife-events-scraper \
  --payload '{"source": "manual", "targets": ["fairfax-library"]}' \
  /tmp/response.json

# Scrape all Pokémon sources only
aws lambda invoke \
  --function-name novakidlife-events-scraper \
  --payload '{"source": "manual", "targets": ["pokemon-tcg-nova-events", "pokemon-tcg-drops", "google-news-pokemon-nova"]}' \
  /tmp/response.json

# View response
cat /tmp/scrape-response.json | python -m json.tool
```

---

## Monitor Scrape Progress

```bash
# Tail CloudWatch logs
aws logs tail /aws/lambda/novakidlife-events-scraper \
  --since 30m \
  --follow

# Check SQS queue depth
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/<account>/novakidlife-events-queue \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible

# Check DLQ (failed events)
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/<account>/novakidlife-events-dlq \
  --attribute-names ApproximateNumberOfMessages
```

---

## Source Registry

Full source list in `services/events-scraper/config/sources.json`:

| Key | Count | Schedule |
|-----|-------|----------|
| `tier1_events` | 4 | Daily |
| `tier2_events` | 12 | Daily |
| `tier3_deals` | 5 | 4×/day or daily |
| `pokemon_events` | 3 | Daily or weekly |

---

## Deduplication

Events are deduplicated in Supabase using a unique constraint on `source_url`.
The publisher does `INSERT ... ON CONFLICT (source_url) DO UPDATE SET updated_at = now()`.
Re-running the same scraper is safe — no duplicate rows are created.
