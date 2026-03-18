"""
content-generator Lambda handler.

Triggers:
  EventBridge schedule — "weekend" (Thursday 8pm EST) and "week_ahead" (Monday 6am EST)
  Also accepts manual invocation: { "trigger": "weekend" | "week_ahead" }
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _bootstrap_secrets() -> None:
    """Load secrets from SSM Parameter Store into env vars."""
    from ssm import get_ssm_parameter
    mappings = {
        "SUPABASE_URL":         "/novakidlife/supabase/url",
        "SUPABASE_SERVICE_KEY": "/novakidlife/supabase/service-key",
        "OPENAI_API_KEY":       "/novakidlife/openai/api-key",
        "GITHUB_TOKEN":         "/novakidlife/github/token",
    }
    for env_key, ssm_path in mappings.items():
        if not os.environ.get(env_key):
            try:
                os.environ[env_key] = get_ssm_parameter(ssm_path)
            except RuntimeError as exc:
                logger.warning("Could not load %s: %s", env_key, exc)


_bootstrap_secrets()


def lambda_handler(event: dict, context) -> dict:
    from openai import OpenAI
    from supabase import create_client

    from post_builder import build_posts_for_trigger
    from github_trigger import trigger_frontend_rebuild

    # Determine trigger type from EventBridge detail or manual invocation
    trigger = (
        event.get("trigger")
        or event.get("detail", {}).get("trigger")
        or _infer_trigger_from_schedule()
    )

    if trigger not in ("weekend", "week_ahead"):
        logger.error("Unknown trigger: %s — must be 'weekend' or 'week_ahead'", trigger)
        return {"statusCode": 400, "body": f"Unknown trigger: {trigger}"}

    logger.info("Starting content generation — trigger: %s", trigger)

    # Init clients
    supabase_url = os.environ["SUPABASE_URL"]
    supabase_key = os.environ["SUPABASE_SERVICE_KEY"]
    openai_key   = os.environ["OPENAI_API_KEY"]

    db     = create_client(supabase_url, supabase_key)
    openai = OpenAI(api_key=openai_key)

    # Generate posts
    saved = build_posts_for_trigger(db, openai, trigger)
    logger.info("Generated %d blog posts", len(saved))

    # Trigger frontend rebuild if any new posts were saved
    rebuild_triggered = False
    if saved:
        rebuild_triggered = trigger_frontend_rebuild()
        if rebuild_triggered:
            logger.info("Frontend rebuild triggered")
        else:
            logger.warning("Frontend rebuild NOT triggered — deploy manually or wait for next scheduled build")

    return {
        "statusCode":       200,
        "posts_generated":  len(saved),
        "slugs":            [p.get("slug") for p in saved],
        "rebuild_triggered": rebuild_triggered,
    }


def _infer_trigger_from_schedule() -> str:
    """Infer trigger type from current day of week when not explicitly provided."""
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo
    now     = datetime.now(ZoneInfo("America/New_York"))
    weekday = now.weekday()  # 0=Mon, 3=Thu
    return "weekend" if weekday == 3 else "week_ahead"


# Alias for Terraform handler config (handler.handler)
handler = lambda_handler
