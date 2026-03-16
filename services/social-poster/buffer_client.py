"""
Ayrshare API client for NovaKidLife social posting.
Wraps the Ayrshare REST API for scheduling posts across platforms.

Ayrshare API docs: https://docs.ayrshare.com
"""
import logging
from dataclasses import dataclass
from enum import Enum

import httpx

logger = logging.getLogger(__name__)

AYRSHARE_API_BASE = "https://app.ayrshare.com/api"


class Platform(str, Enum):
    TWITTER   = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK  = "facebook"


@dataclass
class SocialPost:
    id:           str
    status:       str
    scheduled_at: str
    text:         str


class AyrshareClient:
    """Thin wrapper around the Ayrshare REST API."""

    def __init__(self, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=AYRSHARE_API_BASE,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            timeout=30,
        )

    def create_post(
        self,
        platform:     Platform,
        text:         str,
        media_url:    str | None = None,
        scheduled_at: str | None = None,
    ) -> SocialPost:
        """Schedule a post to a single platform.

        Args:
            platform:     Target platform.
            text:         Post copy (platform-appropriate).
            media_url:    Public image URL.
            scheduled_at: ISO 8601 datetime string (UTC). Posts immediately if omitted.

        Returns:
            SocialPost with post ID and status.
        """
        payload: dict = {
            "post":      text,
            "platforms": [platform.value],
        }
        if media_url:
            payload["mediaUrls"] = [media_url]
        if scheduled_at:
            payload["scheduleDate"] = scheduled_at

        resp = self._client.post("/post", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return SocialPost(
            id=data.get("id", ""),
            status=data.get("status", "success"),
            scheduled_at=scheduled_at or "",
            text=text,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
