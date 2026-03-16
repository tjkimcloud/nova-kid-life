"""
Tests for the Lambda router — path matching, CORS, error handling.
No DB or external calls required.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import pytest
from router import Router, ok, error


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_event(method: str, path: str, qs: dict = None, body: dict = None) -> dict:
    return {
        "httpMethod":            method,
        "path":                  path,
        "queryStringParameters": qs,
        "headers":               {"Content-Type": "application/json"},
        "body":                  json.dumps(body) if body else None,
    }


# ── ok / error helpers ─────────────────────────────────────────────────────────

class TestResponseHelpers:
    def test_ok_status_200(self):
        r = ok({"key": "value"})
        assert r["statusCode"] == 200

    def test_ok_body_json(self):
        r = ok({"key": "value"})
        assert json.loads(r["body"]) == {"key": "value"}

    def test_ok_cors_header(self):
        r = ok({})
        assert "Access-Control-Allow-Origin" in r["headers"]

    def test_ok_custom_status(self):
        r = ok({}, status=201)
        assert r["statusCode"] == 201

    def test_error_status(self):
        r = error("oops", 404)
        assert r["statusCode"] == 404

    def test_error_body(self):
        r = error("oops", 404)
        assert json.loads(r["body"]) == {"error": "oops"}


# ── Router dispatch ────────────────────────────────────────────────────────────

class TestRouter:
    def setup_method(self):
        self.router = Router()

        @self.router.get("/health")
        def health(event, ctx):
            return ok({"status": "ok"})

        @self.router.get("/events/{slug}")
        def get_event(event, ctx):
            slug = event["pathParameters"]["slug"]
            return ok({"slug": slug})

        @self.router.post("/events/search")
        def search(event, ctx):
            return ok({"results": []})

    def test_get_health(self):
        r = self.router.dispatch(make_event("GET", "/health"), None)
        assert r["statusCode"] == 200
        assert json.loads(r["body"])["status"] == "ok"

    def test_path_param_extraction(self):
        r = self.router.dispatch(make_event("GET", "/events/my-event-slug"), None)
        assert r["statusCode"] == 200
        assert json.loads(r["body"])["slug"] == "my-event-slug"

    def test_post_route(self):
        r = self.router.dispatch(make_event("POST", "/events/search", body={"query": "test"}), None)
        assert r["statusCode"] == 200

    def test_404_unknown_path(self):
        r = self.router.dispatch(make_event("GET", "/nonexistent"), None)
        assert r["statusCode"] == 404

    def test_404_wrong_method(self):
        r = self.router.dispatch(make_event("POST", "/health"), None)
        assert r["statusCode"] == 404

    def test_cors_preflight(self):
        r = self.router.dispatch(make_event("OPTIONS", "/events"), None)
        assert r["statusCode"] == 204
        assert "Access-Control-Allow-Origin" in r["headers"]

    def test_handler_exception_returns_500(self):
        @self.router.get("/boom")
        def boom(event, ctx):
            raise RuntimeError("kaboom")

        r = self.router.dispatch(make_event("GET", "/boom"), None)
        assert r["statusCode"] == 500


# ── Models ─────────────────────────────────────────────────────────────────────

class TestModels:
    def test_search_request_valid(self):
        from models import SearchRequest
        req = SearchRequest(query="pokemon events fairfax", limit=5)
        assert req.query == "pokemon events fairfax"
        assert req.limit == 5

    def test_search_request_empty_query_raises(self):
        from models import SearchRequest
        with pytest.raises(Exception):
            SearchRequest(query="   ")

    def test_search_request_limit_capped_at_50(self):
        from models import SearchRequest
        req = SearchRequest(query="test", limit=999)
        assert req.limit == 50

    def test_search_request_limit_minimum_1(self):
        from models import SearchRequest
        req = SearchRequest(query="test", limit=0)
        assert req.limit == 1

    def test_newsletter_valid_email(self):
        from models import NewsletterSubscribeRequest
        req = NewsletterSubscribeRequest(email="test@example.com")
        assert req.email == "test@example.com"

    def test_newsletter_invalid_email_raises(self):
        from models import NewsletterSubscribeRequest
        with pytest.raises(Exception):
            NewsletterSubscribeRequest(email="not-an-email")

    def test_event_to_response_removes_embedding(self):
        from models import event_to_response
        row = {"id": "1", "title": "Test", "embedding": [0.1, 0.2, 0.3]}
        result = event_to_response(row)
        assert "embedding" not in result
        assert result["title"] == "Test"

    def test_event_to_response_renames_columns(self):
        from models import event_to_response
        row = {
            "id": "1",
            "title": "Test",
            "venue_name": "Fairfax Library",
            "address": "10360 North St, Fairfax, VA",
            "full_description": "A great event.",
            "short_description": "Great.",
        }
        result = event_to_response(row)
        assert result["location_name"]    == "Fairfax Library"
        assert result["location_address"] == "10360 North St, Fairfax, VA"
        assert result["description"]      == "A great event."
        assert "venue_name"        not in result
        assert "address"           not in result
        assert "full_description"  not in result
        assert "short_description" not in result

    def test_paginated_has_more_true(self):
        from models import paginated
        result = paginated([], total=100, limit=20, offset=0)
        assert result["has_more"] is True

    def test_paginated_has_more_false_at_end(self):
        from models import paginated
        result = paginated([], total=20, limit=20, offset=0)
        assert result["has_more"] is False
