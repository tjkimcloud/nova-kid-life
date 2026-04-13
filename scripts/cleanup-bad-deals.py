"""
One-shot cleanup script: remove stale / off-topic deals from Supabase cloud.

Targets:
  1. Events whose start_at is in the past (Easter, etc.) — Tier 2 AI sometimes
     ignores the "upcoming only" instruction when source pages still list them.
  2. Deals from hip2save / krazy-coupon-lady whose titles contain explicit
     non-NoVa city names — the old prompt had no geographic filter.

Usage (from repo root):
  python scripts/cleanup-bad-deals.py [--dry-run]

Requires SUPABASE_URL + SUPABASE_KEY (or SUPABASE_SERVICE_KEY) in environment,
OR a .env file at the repo root.
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap .env if present
# ---------------------------------------------------------------------------
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set.", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# City patterns that flag a deal as NOT Northern Virginia
# (case-insensitive substring match against the event title)
# ---------------------------------------------------------------------------
NON_NOVA_CITY_PATTERNS = [
    "in louisville",
    "in indianapolis",
    "in chicago",
    "in houston",
    "in dallas",
    "in atlanta",
    "in miami",
    "in denver",
    "in phoenix",
    "in seattle",
    "in portland",
    "in boston",
    "in nashville",
    "in charlotte",
    "in memphis",
    "in st. louis",
    "in minneapolis",
    "in kansas city",
    "in new orleans",
    "in los angeles",
    "in san francisco",
    "in san diego",
    "in las vegas",
]

# Sources that handle geographic deals
DEAL_SOURCES = {"hip2save", "krazy-coupon-lady"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _get(path: str) -> list[dict]:
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{path}"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def _delete_by_ids(ids: list[str], dry_run: bool) -> int:
    if not ids:
        return 0
    if dry_run:
        print(f"  [dry-run] would delete {len(ids)} rows")
        return len(ids)

    # Supabase REST: DELETE /events?id=in.(id1,id2,...)
    id_list = ",".join(ids)
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/events?id=in.({id_list})"
    req = urllib.request.Request(url, method="DELETE", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=15):
            pass
        return len(ids)
    except Exception as exc:
        print(f"  ERROR deleting: {exc}", file=sys.stderr)
        return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Clean up bad deals from Supabase")
    parser.add_argument("--dry-run", action="store_true", help="List rows to delete without actually deleting")
    args = parser.parse_args()

    today = datetime.now(timezone.utc).date().isoformat()
    to_delete: list[tuple[str, str, str]] = []  # (id, title, reason)

    print(f"Fetching published events (today = {today}) ...")

    # ── 1. Past events that slipped through (start_at < today) ────────────────
    path = (
        "events?status=eq.published"
        "&section=eq.main"
        f"&start_at=lt.{today}"
        "&select=id,title,start_at,event_type,source_name"
        "&limit=500"
    )
    past_events = _get(path)
    for row in past_events:
        reason = f"start_at {row['start_at'][:10]} is in the past"
        to_delete.append((row["id"], row["title"], reason))

    print(f"  Found {len(past_events)} events with past start_at")

    # ── 2. Deals with non-NoVa city names in the title ─────────────────────────
    # Fetch all active deals from our two deal scrapers
    deal_path = (
        "events?status=eq.published"
        "&section=eq.main"
        "&event_type=in.(deal,birthday_freebie,product_drop)"
        "&select=id,title,source_name,start_at"
        "&limit=500"
    )
    all_deals = _get(deal_path)
    geo_bad = []
    for row in all_deals:
        title_lower = row.get("title", "").lower()
        for pattern in NON_NOVA_CITY_PATTERNS:
            if pattern in title_lower:
                geo_bad.append((row["id"], row["title"], f"non-NoVa city pattern: '{pattern}'"))
                break
    to_delete.extend(geo_bad)
    print(f"  Found {len(geo_bad)} deals with non-NoVa city patterns")

    # ── 3. Deduplicate ─────────────────────────────────────────────────────────
    seen_ids: set[str] = set()
    unique: list[tuple[str, str, str]] = []
    for item in to_delete:
        if item[0] not in seen_ids:
            seen_ids.add(item[0])
            unique.append(item)
    to_delete = unique

    if not to_delete:
        print("Nothing to clean up.")
        return

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Cleaning up {len(to_delete)} row(s):")
    for event_id, title, reason in to_delete:
        print(f"  - {title!r} ({reason})")

    ids = [item[0] for item in to_delete]
    deleted = _delete_by_ids(ids, dry_run=args.dry_run)
    print(f"\n{'Would delete' if args.dry_run else 'Deleted'} {deleted} row(s).")


if __name__ == "__main__":
    main()
