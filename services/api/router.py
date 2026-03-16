"""
Lightweight Lambda router for API Gateway proxy integration.

Usage:
    router = Router()

    @router.get("/events")
    def list_events(event, ctx): ...

    @router.post("/events/search")
    def search_events(event, ctx): ...

    def lambda_handler(event, context):
        return router.dispatch(event, context)
"""
from __future__ import annotations

import json
import logging
import re
from typing import Callable

logger = logging.getLogger(__name__)

# CORS headers added to every response
_CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "https://www.novakidlife.com",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Api-Key",
    "Content-Type": "application/json",
}


def ok(body: dict | list, status: int = 200) -> dict:
    return {
        "statusCode": status,
        "headers":    _CORS_HEADERS,
        "body":       json.dumps(body, default=str),
    }


def error(message: str, status: int = 400) -> dict:
    return {
        "statusCode": status,
        "headers":    _CORS_HEADERS,
        "body":       json.dumps({"error": message}),
    }


def _path_to_regex(path: str) -> tuple[re.Pattern, list[str]]:
    """Convert '/events/{slug}' to a regex with named groups."""
    params = re.findall(r"\{(\w+)\}", path)
    pattern = re.sub(r"\{\w+\}", r"([^/]+)", path)
    return re.compile(f"^{pattern}$"), params


class Router:
    def __init__(self):
        self._routes: list[tuple[str, re.Pattern, list[str], Callable]] = []

    def _add(self, method: str, path: str, fn: Callable) -> None:
        regex, params = _path_to_regex(path)
        self._routes.append((method.upper(), regex, params, fn))

    def get(self, path: str):
        def decorator(fn):
            self._add("GET", path, fn)
            return fn
        return decorator

    def post(self, path: str):
        def decorator(fn):
            self._add("POST", path, fn)
            return fn
        return decorator

    def dispatch(self, event: dict, context) -> dict:
        method = event.get("httpMethod", "GET").upper()
        path   = event.get("path", "/")

        # Handle CORS preflight
        if method == "OPTIONS":
            return {"statusCode": 204, "headers": _CORS_HEADERS, "body": ""}

        for route_method, regex, param_names, handler in self._routes:
            if route_method != method:
                continue
            match = regex.match(path)
            if match:
                # Inject path params into event for convenience
                event["pathParameters"] = dict(zip(param_names, match.groups()))
                try:
                    return handler(event, context)
                except Exception as exc:
                    logger.exception("Handler error: %s", exc)
                    return error("Internal server error", 500)

        return error(f"Not found: {method} {path}", 404)
