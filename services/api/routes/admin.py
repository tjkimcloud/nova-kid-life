"""
Admin endpoints — protected by X-Api-Key header.

  POST /admin/events/trigger-scrape   — invoke events-scraper Lambda
  GET  /admin/health/detailed         — full system health with DB + queue stats
"""
from __future__ import annotations

import json
import os

import boto3

from db import get_client
from router import ok, error

_ADMIN_API_KEY       = os.getenv("ADMIN_API_KEY", "")
_SCRAPER_LAMBDA_NAME = os.getenv("SCRAPER_LAMBDA_NAME", "novakidlife-events-scraper")
_EVENTS_QUEUE_URL    = os.getenv("EVENTS_QUEUE_URL", "")


def _require_api_key(event: dict) -> bool:
    """Return True if request carries a valid admin API key."""
    if not _ADMIN_API_KEY:
        return False  # no key configured → locked out
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    return headers.get("x-api-key") == _ADMIN_API_KEY


# ── POST /admin/events/trigger-scrape ─────────────────────────────────────────

def trigger_scrape(event: dict, ctx) -> dict:
    if not _require_api_key(event):
        return error("Unauthorized", 401)

    body    = json.loads(event.get("body") or "{}")
    targets = body.get("targets", ["all"])

    payload = json.dumps({
        "source":  "admin_api",
        "targets": targets,
    })

    try:
        client  = boto3.client("lambda")
        resp    = client.invoke(
            FunctionName    = _SCRAPER_LAMBDA_NAME,
            InvocationType  = "Event",   # async fire-and-forget
            Payload         = payload.encode(),
        )
        status_code = resp.get("StatusCode", 0)
        if status_code != 202:
            return error(f"Lambda invoke returned {status_code}", 500)
    except Exception as exc:
        return error(f"Failed to invoke scraper: {exc}", 500)

    return ok({
        "message": "Scrape triggered",
        "targets": targets,
    })


# ── GET /admin/health/detailed ────────────────────────────────────────────────

def detailed_health(event: dict, ctx) -> dict:
    if not _require_api_key(event):
        return error("Unauthorized", 401)

    health: dict = {
        "status":   "ok",
        "database": {},
        "queues":   {},
        "counts":   {},
    }

    # DB health + row counts
    db = get_client()
    try:
        for table in ("events", "categories", "locations", "newsletter_subs"):
            resp = db.table(table).select("id", count="exact").execute()
            health["counts"][table] = resp.count or 0
        health["database"]["status"] = "ok"
    except Exception as exc:
        health["database"] = {"status": "error", "error": str(exc)}
        health["status"]   = "degraded"

    # Section counts
    try:
        for section in ("main", "pokemon"):
            resp = (
                db.table("events")
                .select("id", count="exact")
                .eq("status", "published")
                .eq("section", section)
                .execute()
            )
            health["counts"][f"published_{section}"] = resp.count or 0
    except Exception:
        pass

    # SQS queue depth
    if _EVENTS_QUEUE_URL:
        try:
            sqs = boto3.client("sqs")
            attrs = sqs.get_queue_attributes(
                QueueUrl       = _EVENTS_QUEUE_URL,
                AttributeNames = [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            )["Attributes"]
            health["queues"]["events_queue"] = {
                "visible":    int(attrs.get("ApproximateNumberOfMessages", 0)),
                "in_flight":  int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
            }
        except Exception as exc:
            health["queues"]["events_queue"] = {"error": str(exc)}

    return ok(health)
