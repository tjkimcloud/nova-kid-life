"""
Buffer API client for NovaKidLife social posting.
Wraps the Buffer v1 REST API used to schedule posts across platforms.

Buffer API docs: https://buffer.com/developers/api
"""
import logging
from dataclasses import dataclass
from enum import Enum

import httpx

logger = logging.getLogger(__name__)

BUFFER_API_BASE = "https://api.bufferapp.com/1"


class Platform(str, Enum):
    TWITTER   = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK  = "facebook"


@dataclass
class BufferProfile:
    id:       str
    service:  str   # "twitter" | "instagram" | "facebook"
    name:     str


@dataclass
class BufferUpdate:
    id:           str
    status:       str   # "buffer" | "sent" | "error"
    scheduled_at: str
    text:         str


class BufferClient:
    """Thin wrapper around the Buffer v1 API."""

    def __init__(self, access_token: str) -> None:
        self._token = access_token
        self._client = httpx.Client(
            base_url=BUFFER_API_BASE,
            timeout=30,
        )

    # ── Profiles ───────────────────────────────────────────────────────────────

    def get_profiles(self) -> list[BufferProfile]:
        """Return all connected Buffer profiles."""
        resp = self._client.get(
            "/profiles.json",
            params={"access_token": self._token},
        )
        resp.raise_for_status()
        return [
            BufferProfile(
                id=p["id"],
                service=p["service"],
                name=p.get("formatted_username", p.get("service_username", "")),
            )
            for p in resp.json()
        ]

    def get_profiles_by_platform(
        self, platforms: list[Platform]
    ) -> dict[Platform, list[str]]:
        """Return a mapping of Platform → list of profile IDs for that platform."""
        all_profiles = self.get_profiles()
        result: dict[Platform, list[str]] = {p: [] for p in platforms}
        for profile in all_profiles:
            for platform in platforms:
                if profile.service == platform.value:
                    result[platform].append(profile.id)
        return result

    # ── Updates ────────────────────────────────────────────────────────────────

    def create_update(
        self,
        profile_ids:  list[str],
        text:         str,
        media_url:    str | None = None,
        scheduled_at: str | None = None,
    ) -> BufferUpdate:
        """Schedule a post to one or more Buffer profiles.

        Args:
            profile_ids:  Buffer profile IDs to post to.
            text:         Post copy (platform-appropriate).
            media_url:    Public URL to an image (1200×630 for Twitter/Facebook,
                          1080×1080 for Instagram).
            scheduled_at: ISO 8601 datetime string. If omitted, Buffer uses
                          optimal timing if enabled, else posts immediately.

        Returns:
            BufferUpdate with update ID and scheduled time.
        """
        payload: dict = {
            "access_token":   self._token,
            "profile_ids[]":  profile_ids,
            "text":           text,
        }
        if media_url:
            payload["media[photo]"] = media_url
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at

        resp = self._client.post("/updates/create.json", data=payload)
        resp.raise_for_status()
        data = resp.json()

        # Buffer returns {success, buffer_count, updates: [...]}
        updates = data.get("updates", [data])
        first   = updates[0] if updates else {}
        return BufferUpdate(
            id=first.get("id", ""),
            status=first.get("status", "buffer"),
            scheduled_at=first.get("scheduled_at", scheduled_at or ""),
            text=text,
        )

    def get_pending_updates(self, profile_id: str) -> list[BufferUpdate]:
        """Return pending scheduled updates for a profile (for queue depth checks)."""
        resp = self._client.get(
            f"/profiles/{profile_id}/updates/pending.json",
            params={"access_token": self._token},
        )
        resp.raise_for_status()
        data = resp.json()
        return [
            BufferUpdate(
                id=u["id"],
                status=u.get("status", "buffer"),
                scheduled_at=u.get("scheduled_at", ""),
                text=u.get("text", ""),
            )
            for u in data.get("updates", [])
        ]

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
