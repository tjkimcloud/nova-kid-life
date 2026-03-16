"""
Seed the local Supabase database with test events.
Usage: python services/api/scripts/seed.py --count 10
Requires: pip install supabase python-dotenv
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from supabase import create_client

load_dotenv("services/api/.env")

SAMPLE_EVENTS = [
    {
        "title": "Fairfax Fall Festival",
        "short_description": "Annual harvest celebration with pumpkin patch and hayrides for the whole family.",
        "location_text": "Fairfax City, VA",
        "age_range": "All ages",
        "tags": ["festival", "outdoor", "seasonal"],
        "is_free": False,
        "source_name": "seed",
    },
    {
        "title": "Reston Children's Museum Free Sunday",
        "short_description": "Free admission every first Sunday. Hands-on exhibits for curious kids.",
        "location_text": "Reston, VA",
        "age_range": "2–10 years",
        "tags": ["museum", "indoor", "educational", "free"],
        "is_free": True,
        "source_name": "seed",
    },
    {
        "title": "Arlington Nature Camp",
        "short_description": "Week-long outdoor nature exploration camp in Long Branch Nature Center.",
        "location_text": "Arlington, VA",
        "age_range": "5–12 years",
        "tags": ["nature", "camps", "outdoor", "educational"],
        "is_free": False,
        "source_name": "seed",
    },
    {
        "title": "Loudoun Storytime & Craft",
        "short_description": "Weekly library storytime followed by a themed craft activity.",
        "location_text": "Leesburg, VA",
        "age_range": "2–6 years",
        "tags": ["library", "arts-crafts", "indoor", "free"],
        "is_free": True,
        "source_name": "seed",
    },
    {
        "title": "NoVa Kids Coding Workshop",
        "short_description": "Intro to Scratch programming. No experience needed — just curiosity!",
        "location_text": "McLean, VA",
        "age_range": "7–12 years",
        "tags": ["educational", "indoor", "technology"],
        "is_free": False,
        "source_name": "seed",
    },
]


def seed(count: int, env: str) -> None:
    if env == "production":
        print("ERROR: Refusing to seed production database.", file=sys.stderr)
        sys.exit(1)

    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    supabase = create_client(url, key)

    now = datetime.now(timezone.utc)
    seeded = 0

    for i in range(count):
        sample = random.choice(SAMPLE_EVENTS)
        start_at = now + timedelta(days=random.randint(1, 60))
        slug = f"{sample['title'].lower().replace(' ', '-')}-seed-{i + 1}"

        event = {
            **sample,
            "slug": slug,
            "title": f"{sample['title']} (seed #{i + 1})",
            "start_at": start_at.isoformat(),
            "end_at": (start_at + timedelta(hours=3)).isoformat(),
            "source_url": f"https://seed.example.com/event/{i + 1}",
            "status": "published",
            "is_published": True,
        }

        result = (
            supabase.table("events")
            .upsert(event, on_conflict="source_url")
            .execute()
        )
        print(f"  [{i + 1}/{count}] {event['title']}")
        seeded += 1

    print(f"\nDone. Seeded {seeded} events.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed NovaKidLife events")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--env", default="development")
    args = parser.parse_args()
    seed(args.count, args.env)
