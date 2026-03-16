"""
Pydantic models for API request validation and response serialization.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, EmailStr, field_validator


# ── Request models ─────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    section: str = "main"

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query cannot be empty")
        return v[:500]  # hard cap

    @field_validator("limit")
    @classmethod
    def limit_range(cls, v: int) -> int:
        return max(1, min(v, 50))


class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr


# ── Response helpers ───────────────────────────────────────────────────────────

def event_to_response(row: dict) -> dict:
    """Strip internal fields and normalize an events row for API output.

    Maps DB column names → frontend field names expected by TypeScript types.
    DB uses: venue_name, address, full_description
    API/TS expects: location_name, location_address, description
    """
    row.pop("embedding", None)

    # Rename DB columns → TypeScript Event interface fields
    row["location_name"]    = row.pop("venue_name",        row.get("location_name", ""))
    row["location_address"] = row.pop("address",           row.get("location_address", None))
    row["description"]      = row.pop("full_description",  row.get("description", ""))

    # Drop internal-only fields not in the TypeScript type
    row.pop("short_description", None)
    row.pop("location_text",     None)
    row.pop("seo_title",         None)
    row.pop("seo_description",   None)
    row.pop("is_published",      None)
    row.pop("recurrence_rule",   None)

    return row


def paginated(items: list, total: int, limit: int, offset: int) -> dict:
    return {
        "items":    items,
        "total":    total,
        "limit":    limit,
        "offset":   offset,
        "has_more": (offset + limit) < total,
    }
