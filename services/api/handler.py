"""
API Lambda handler — all REST endpoints for novakidlife.com.

Endpoints:
  GET  /health
  GET  /events
  GET  /events/featured
  GET  /events/upcoming
  GET  /events/{slug}
  POST /events/search
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

from router import Router, ok

# Route handlers
from routes.events     import list_events, featured_events, upcoming_events, get_event, search_events
from routes.pokemon    import pokemon_events, pokemon_drops, pokemon_retailers
from routes.categories import list_categories
from routes.locations  import list_locations
from routes.newsletter import subscribe
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
