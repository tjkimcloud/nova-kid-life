"""
API Lambda handler — all REST endpoints for novakidlife.com.

Endpoints:
  GET  /health
  GET  /events
  GET  /events/featured
  GET  /events/upcoming
  GET  /events/{slug}
  POST /events/search
  GET  /blog
  GET  /blog/{slug}
  GET  /categories
  GET  /locations
  GET  /pokemon/events
  GET  /pokemon/drops
  GET  /pokemon/retailers
  POST /newsletter/subscribe
  GET  /sitemap
  POST /admin/events/trigger-scrape   (X-Api-Key required)
  GET  /admin/health/detailed         (X-Api-Key required)
"""
from __future__ import annotations

import json
import logging
import os


def _load_secrets_from_ssm() -> None:
    """Resolve *_PARAM env vars from SSM into their canonical env var names."""
    param_map = {
        "SUPABASE_URL_PARAM":   "SUPABASE_URL",
        "SUPABASE_KEY_PARAM":   "SUPABASE_SERVICE_KEY",
        "OPENAI_API_KEY_PARAM": "OPENAI_API_KEY",
        "ADMIN_API_KEY_PARAM":  "ADMIN_API_KEY",
    }
    ssm_paths = {v: os.environ[k] for k, v in param_map.items() if k in os.environ}
    if not ssm_paths:
        return
    try:
        import boto3
        ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        for env_key, param_path in ssm_paths.items():
            if not os.environ.get(env_key):
                result = ssm.get_parameter(Name=param_path, WithDecryption=True)
                os.environ[env_key] = result["Parameter"]["Value"]
    except Exception as exc:
        logging.getLogger(__name__).warning("SSM bootstrap warning: %s", exc)


_load_secrets_from_ssm()

from router import Router, ok

# Route handlers
from routes.events     import list_events, featured_events, upcoming_events, get_event, search_events
from routes.pokemon    import pokemon_events, pokemon_drops, pokemon_retailers
from routes.categories import list_categories
from routes.locations  import list_locations
from routes.newsletter import subscribe
from routes.blog       import list_blog_posts, get_blog_post
from routes.sitemap    import get_sitemap
from routes.admin      import trigger_scrape, detailed_health

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ── Register routes ────────────────────────────────────────────────────────────

router = Router()

# Health
@router.get("/health")
def health(event, ctx):
    return ok({"status": "ok", "service": "novakidlife-api"})

# Events
router.get("/events")(list_events)
router.get("/events/featured")(featured_events)
router.get("/events/upcoming")(upcoming_events)
router.get("/events/{slug}")(get_event)
router.post("/events/search")(search_events)

# Pokémon TCG section
router.get("/pokemon/events")(pokemon_events)
router.get("/pokemon/drops")(pokemon_drops)
router.get("/pokemon/retailers")(pokemon_retailers)

# Blog
router.get("/blog")(list_blog_posts)
router.get("/blog/{slug}")(get_blog_post)

# Reference data
router.get("/categories")(list_categories)
router.get("/locations")(list_locations)

# Newsletter
router.post("/newsletter/subscribe")(subscribe)

# Sitemap (used by Next.js build)
router.get("/sitemap")(get_sitemap)

# Admin (API key protected)
router.post("/admin/events/trigger-scrape")(trigger_scrape)
router.get("/admin/health/detailed")(detailed_health)


# ── Lambda entry point ─────────────────────────────────────────────────────────

def lambda_handler(event: dict, context) -> dict:
    method = event.get("httpMethod", "?")
    path   = event.get("path", "/")
    logger.info("%s %s", method, path)
    return router.dispatch(event, context)

# Alias for Terraform handler config (handler.handler)
handler = lambda_handler
