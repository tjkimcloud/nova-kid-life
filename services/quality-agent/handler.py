"""
quality-agent Lambda — post-scrape event filter + source scorecard.

Triggered by: EventBridge (daily 6:15 AM EST, 15 min after scraper)
              or manual: {"mode": "full"} | {"mode": "score_only"}

What it does:
1. Pulls all events published in the last 24h (status='published')
2. Scores each for NoVA relevance using Claude Haiku (fast + cheap)
3. Unpublishes events below threshold (marks status='filtered')
4. Updates scraper_metrics per source (quality scores, event counts)
5. Auto-flags sources with nova_score < 0.25 for 3+ consecutive weeks
6. Logs removed events to quality_filter_log for tuning over time
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone, timedelta

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_SUPABASE_URL = ""
_SUPABASE_KEY = ""
_client: OpenAI | None = None

# NoVA counties + independent cities for relevance check
_NOVA_KEYWORDS = [
    "fairfax", "arlington", "loudoun", "prince william", "alexandria",
    "reston", "herndon", "mclean", "vienna", "falls church", "leesburg",
    "ashburn", "sterling", "chantilly", "centreville", "manassas",
    "woodbridge", "dale city", "stafford", "fredericksburg",
    "tysons", "burke", "springfield", "annandale", "great falls",
    "potomac falls", "south riding", "dulles", "nova", "northern virginia",
    "washington dc", "washington, dc", "dmv", "dc metro",
]

_RELEVANCE_SYSTEM = """You are a relevance filter for NovaKidLife, a family events platform
serving Northern Virginia (NoVA) — Fairfax, Arlington, Loudoun, Prince William counties
and cities including Alexandria, Reston, Herndon, McLean, Vienna, Falls Church, Leesburg,
Ashburn, Sterling, Chantilly, Centreville, Manassas, Woodbridge, Dulles.

Evaluate whether each event should appear on this site.

Respond with a JSON array, one object per event, in the same order:
[
  {
    "id": "<event id>",
    "score": <0.0 to 1.0>,
    "keep": <true|false>,
    "reason": "<one sentence>"
  }
]

Scoring guide:
- 0.9–1.0: Clearly NoVA event with specific venue/location
- 0.6–0.8: Likely NoVA or broader DC-metro, appropriate for families
- 0.3–0.5: National deal/freebie with potential local relevance (keep borderline)
- 0.0–0.2: Wrong geography (Louisville, etc.) OR completely irrelevant to families

Set keep=false only for score < 0.3.
National kids deals from major chains (Chick-fil-A, etc.) score 0.4 — borderline keep=true."""


def _load_secrets() -> None:
    global _SUPABASE_URL, _SUPABASE_KEY, _ANTHROPIC_KEY
    param_map = {
        "SUPABASE_URL_PARAM":   "SUPABASE_URL",
        "SUPABASE_KEY_PARAM":   "SUPABASE_SERVICE_KEY",
        "OPENAI_API_KEY_PARAM": "OPENAI_API_KEY",
    }
    ssm_paths = {v: os.environ[k] for k, v in param_map.items() if k in os.environ}
    if ssm_paths:
        try:
            import boto3
            ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
            for env_key, path in ssm_paths.items():
                if not os.environ.get(env_key):
                    result = ssm.get_parameter(Name=path, WithDecryption=True)
                    os.environ[env_key] = result["Parameter"]["Value"]
        except Exception as exc:
            logger.warning("SSM load warning: %s", exc)

    _SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    _SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


_load_secrets()


def _sb_headers() -> dict:
    return {
        "apikey":        _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type":  "application/json",
    }


def _get_openai() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    return _client


def _fetch_recent_events(hours: int = 26) -> list[dict]:
    """Fetch published events with start_at in the future or recent past (last 7 days).
    This covers both newly-scraped upcoming events and any that slipped through.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    resp = httpx.get(
        f"{_SUPABASE_URL}/rest/v1/events",
        params={
            "select": "id,title,full_description,location_text,venue_name,address,source_url,section,start_at,event_type,tags,status",
            "status": "eq.published",
            "start_at": f"gte.{since}",
            "order": "source_url",
            "limit": "500",
        },
        headers=_sb_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _quick_nova_check(event: dict) -> bool:
    """Fast keyword check before calling AI — skip AI for obviously local events."""
    text = " ".join([
        event.get("title", ""),
        event.get("location_text", ""),
        event.get("venue_name", ""),
        event.get("address", ""),
        event.get("description", "")[:200],
    ]).lower()
    return any(kw in text for kw in _NOVA_KEYWORDS)


def _score_events_with_ai(events: list[dict]) -> list[dict]:
    """Score a batch of events for NoVA relevance using Claude Haiku."""
    if not events:
        return []

    # Build compact event list for AI
    payload = []
    for e in events:
        payload.append({
            "id": e["id"],
            "title": e["title"],
            "location": e.get("location_text") or e.get("venue_name") or "",
            "description": (e.get("full_description") or "")[:300],
            "source": e.get("source_url", "")[:80],
            "type": e.get("event_type", ""),
        })

    try:
        response = _get_openai().chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _RELEVANCE_SYSTEM + "\n\nReturn: {\"results\": [...array...]}"},
                {"role": "user", "content": json.dumps(payload)},
            ],
            max_tokens=2000,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)
        return parsed.get("results", parsed) if isinstance(parsed, dict) else parsed
    except Exception as exc:
        logger.error("AI scoring failed: %s", exc)
        return []


def _unpublish_event(event_id: str, source_name: str, title: str,
                     reason: str, score: float, reasoning: str) -> None:
    """Mark event as filtered and log it."""
    # Update event status
    httpx.patch(
        f"{_SUPABASE_URL}/rest/v1/events?id=eq.{event_id}",
        json={"status": "filtered"},
        headers=_sb_headers(),
        timeout=10,
    )
    # Log to quality_filter_log
    httpx.post(
        f"{_SUPABASE_URL}/rest/v1/quality_filter_log",
        json={
            "event_id": event_id,
            "source_name": source_name,
            "title": title,
            "reason": reason,
            "ai_score": score,
            "ai_reasoning": reasoning,
        },
        headers={**_sb_headers(), "Prefer": "return=minimal"},
        timeout=10,
    )


def _update_source_metrics(
    source_name: str,
    scraped: int,
    published: int,
    removed: int,
    nova_score: float,
) -> None:
    """Upsert source metrics — rolling average nova score."""
    # Fetch existing row
    resp = httpx.get(
        f"{_SUPABASE_URL}/rest/v1/scraper_metrics?source_name=eq.{source_name}",
        headers=_sb_headers(),
        timeout=10,
    )
    existing = resp.json()[0] if resp.json() else {}

    old_runs = existing.get("total_runs", 0)
    old_score = existing.get("nova_relevance_score") or nova_score
    # Rolling average
    new_score = round((old_score * old_runs + nova_score) / (old_runs + 1), 3)
    consec_fail = existing.get("consecutive_failures", 0)
    if scraped > 0:
        consec_fail = 0
    else:
        consec_fail += 1

    # Auto-flag if score consistently low
    status = existing.get("status", "active")
    flag_reason = existing.get("flag_reason")
    if new_score < 0.25 and old_runs >= 3 and status == "active":
        status = "flagged"
        flag_reason = f"nova_score={new_score:.2f} after {old_runs + 1} runs"
        logger.warning("[%s] AUTO-FLAGGED: low NoVA relevance (score=%.2f)", source_name, new_score)
    if consec_fail >= 5 and status == "active":
        status = "flagged"
        flag_reason = f"5 consecutive failures"
        logger.warning("[%s] AUTO-FLAGGED: 5 consecutive failures", source_name)

    avg_events = round(
        ((existing.get("avg_events_per_run") or 0) * old_runs + scraped) / (old_runs + 1), 1
    )

    httpx.post(
        f"{_SUPABASE_URL}/rest/v1/scraper_metrics?on_conflict=source_name",
        json={
            "source_name": source_name,
            "total_runs": old_runs + 1,
            "total_scraped": existing.get("total_scraped", 0) + scraped,
            "total_published": existing.get("total_published", 0) + published,
            "total_removed": existing.get("total_removed", 0) + removed,
            "consecutive_failures": consec_fail,
            "nova_relevance_score": new_score,
            "avg_events_per_run": avg_events,
            "status": status,
            "flag_reason": flag_reason,
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "last_success_at": datetime.now(timezone.utc).isoformat() if scraped > 0 else existing.get("last_success_at"),
            "last_flagged_at": datetime.now(timezone.utc).isoformat() if status == "flagged" else existing.get("last_flagged_at"),
        },
        headers={**_sb_headers(), "Prefer": "resolution=merge-duplicates,return=minimal"},
        timeout=10,
    )


def handler(event: dict, context) -> dict:
    logger.info("Quality agent invoked: %s", json.dumps(event))
    mode = event.get("mode", "full")

    if not _SUPABASE_URL or not _SUPABASE_KEY:
        return {"statusCode": 500, "body": "Supabase credentials missing"}

    # Fetch events from last scrape run
    hours = event.get("hours", 26)
    events = _fetch_recent_events(hours=hours)
    logger.info("Fetched %d recently published events to evaluate", len(events))

    if not events:
        return {"statusCode": 200, "body": json.dumps({"message": "No new events to evaluate"})}

    # Split: quick keyword pass first (avoid unnecessary AI calls)
    keyword_pass = []
    needs_ai = []
    for e in events:
        if _quick_nova_check(e):
            keyword_pass.append(e)
        else:
            needs_ai.append(e)

    logger.info("Quick check: %d passed, %d need AI evaluation", len(keyword_pass), len(needs_ai))

    # AI-score the uncertain ones in batches of 20
    ai_results: dict[str, dict] = {}
    BATCH = 20
    for i in range(0, len(needs_ai), BATCH):
        batch = needs_ai[i:i + BATCH]
        scores = _score_events_with_ai(batch)
        for s in scores:
            ai_results[s["id"]] = s

    # Process results
    stats = {"total": len(events), "kept": 0, "removed": 0, "ai_calls": len(needs_ai)}
    source_stats: dict[str, dict] = {}

    for e in events:
        eid = e["id"]
        source = e.get("source_url", "unknown")[:60]
        title = e.get("title", "")

        # Determine source_name from source_url domain
        try:
            from urllib.parse import urlparse
            domain = urlparse(source).netloc.replace("www.", "")
            source_name = domain or source[:30]
        except Exception:
            source_name = source[:30]

        if source_name not in source_stats:
            source_stats[source_name] = {"scraped": 0, "published": 0, "removed": 0, "scores": []}
        source_stats[source_name]["scraped"] += 1

        # Decide keep/remove
        if eid in ai_results:
            result = ai_results[eid]
            score = result.get("score", 0.5)
            keep = result.get("keep", True)
            reasoning = result.get("reason", "")
        else:
            # Passed keyword check → keep with high score
            score = 0.85
            keep = True
            reasoning = "keyword match"

        source_stats[source_name]["scores"].append(score)

        if keep:
            stats["kept"] += 1
            source_stats[source_name]["published"] += 1
        else:
            stats["removed"] += 1
            source_stats[source_name]["removed"] += 1
            reason = "not_nova" if score < 0.3 else "low_quality"
            logger.info("[REMOVE] %s (score=%.2f): %s", title[:50], score, reasoning)
            if mode == "full":
                _unpublish_event(eid, source_name, title, reason, score, reasoning)

    # Update source metrics
    for source_name, s in source_stats.items():
        avg_score = sum(s["scores"]) / len(s["scores"]) if s["scores"] else 0.5
        _update_source_metrics(
            source_name=source_name,
            scraped=s["scraped"],
            published=s["published"],
            removed=s["removed"],
            nova_score=avg_score,
        )

    logger.info(
        "Quality pass complete: total=%d kept=%d removed=%d ai_calls=%d",
        stats["total"], stats["kept"], stats["removed"], stats["ai_calls"],
    )

    return {"statusCode": 200, "body": json.dumps(stats)}
