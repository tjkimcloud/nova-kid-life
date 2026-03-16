"""
POST /newsletter/subscribe
"""
from __future__ import annotations

import json

from db import get_client
from models import NewsletterSubscribeRequest
from router import ok, error


def subscribe(event: dict, ctx) -> dict:
    body = json.loads(event.get("body") or "{}")

    try:
        req = NewsletterSubscribeRequest(**body)
    except Exception as exc:
        return error(str(exc), 400)

    db = get_client()

    # Upsert — re-subscribing the same email is a no-op
    resp = (
        db.table("newsletter_subs")
        .upsert({"email": req.email}, on_conflict="email")
        .execute()
    )

    return ok({"message": "Subscribed successfully", "email": req.email}, status=201)
