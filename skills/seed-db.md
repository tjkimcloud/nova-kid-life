# Skill: Seed Database

**Purpose:** Populate Supabase with realistic test event data for development and staging.

## Prerequisites
- `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in environment
- Database schema already migrated (`db-migrate.md`)

## Quick Seed (Python script)

```bash
cd services/api
python scripts/seed.py --count 20 --env development
```

## Seed Script Template

```python
# services/api/scripts/seed.py
import argparse
import json
import random
from datetime import datetime, timedelta
from supabase import create_client

SAMPLE_EVENTS = [
    {
        "title": "Fairfax Fall Festival",
        "short_description": "Annual harvest celebration with pumpkin patch and hayrides.",
        "location": "Fairfax City, VA",
        "age_range": "All ages",
        "tags": ["festival", "outdoor", "seasonal"],
    },
    {
        "title": "Reston Children's Museum Free Weekend",
        "short_description": "Free admission every first Sunday of the month.",
        "location": "Reston, VA",
        "age_range": "2-10 years",
        "tags": ["museum", "indoor", "educational", "free"],
    },
    # Add more sample events here...
]

def seed(count: int, env: str):
    import os
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    supabase = create_client(url, key)

    now = datetime.now()

    for i in range(count):
        sample = random.choice(SAMPLE_EVENTS)
        start_at = now + timedelta(days=random.randint(1, 30))

        event = {
            **sample,
            "title": f"{sample['title']} #{i+1}",
            "start_at": start_at.isoformat(),
            "end_at": (start_at + timedelta(hours=3)).isoformat(),
            "source_url": f"https://example.com/event/{i+1}",
            "is_published": True,
        }

        result = supabase.table("events").upsert(
            event,
            on_conflict="source_url"
        ).execute()

        print(f"Seeded event {i+1}: {event['title']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--env", default="development")
    args = parser.parse_args()
    seed(args.count, args.env)
```

## Clear Seed Data

```sql
-- Run in Supabase SQL Editor (development only)
DELETE FROM events WHERE source_url LIKE 'https://example.com/%';
```

Or via CLI:
```bash
psql "$SUPABASE_DB_URL" -c "DELETE FROM events WHERE source_url LIKE 'https://example.com/%';"
```

## Production Note
Never run seed scripts against production. Use `--env` flag check:
```python
if env == "production":
    raise ValueError("Refusing to seed production database")
```
