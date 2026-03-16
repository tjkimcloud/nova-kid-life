"""
AI image generation — Imagen 3 primary, DALL-E 3 fallback.

Both providers return raw PNG/JPEG bytes that are passed directly
to the enhancer and processor pipelines.
"""
from __future__ import annotations

import base64
import os
from typing import Literal

import httpx

_OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
_GOOGLE_PROJECT    = os.getenv("GOOGLE_PROJECT_ID", "")
_GOOGLE_LOCATION   = os.getenv("GOOGLE_LOCATION", "us-central1")
_GOOGLE_SA_JSON    = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")  # path to key file

ImageSize = Literal["website", "social"]

# DALL-E 3 size strings
_DALLE_SIZE: dict[ImageSize, str] = {
    "website": "1792x1024",   # closest to 16:9 hero
    "social":  "1024x1024",   # square for social
}


# ── Google Vertex AI — Imagen 3 ────────────────────────────────────────────────

def _imagen3_generate(prompt: str, size: ImageSize) -> bytes | None:
    """Call Imagen 3 via Vertex AI REST API. Returns raw PNG bytes or None."""
    if not _GOOGLE_PROJECT:
        return None

    # Set up credentials
    try:
        import google.auth
        import google.auth.transport.requests

        if _GOOGLE_SA_JSON:
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_file(
                _GOOGLE_SA_JSON,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        else:
            creds, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )

        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        token = creds.token
    except Exception:
        return None

    aspect_ratio = "16:9" if size == "website" else "1:1"

    url = (
        f"https://{_GOOGLE_LOCATION}-aiplatform.googleapis.com/v1/projects/"
        f"{_GOOGLE_PROJECT}/locations/{_GOOGLE_LOCATION}/publishers/google/"
        f"models/imagen-3.0-generate-001:predict"
    )

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
            "safetyFilterLevel": "block_some",
            "personGeneration": "allow_adult",
        },
    }

    try:
        resp = httpx.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        b64 = data["predictions"][0]["bytesBase64Encoded"]
        return base64.b64decode(b64)
    except Exception:
        return None


# ── OpenAI — DALL-E 3 ─────────────────────────────────────────────────────────

def _dalle3_generate(prompt: str, size: ImageSize) -> bytes | None:
    """Call DALL-E 3 via OpenAI API. Returns raw PNG bytes or None."""
    if not _OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=_OPENAI_API_KEY)

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=_DALLE_SIZE[size],
            quality="hd",
            response_format="b64_json",
            n=1,
        )
        b64 = response.data[0].b64_json
        return base64.b64decode(b64)
    except Exception:
        return None


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_image(prompt: str, size: ImageSize = "website") -> bytes:
    """
    Generate an image from a prompt.

    Tries Imagen 3 first, falls back to DALL-E 3.
    Raises RuntimeError if both providers fail.

    Args:
        prompt: Full prompt string (from prompts.py)
        size: "website" (16:9 hero) or "social" (1:1 illustration)

    Returns:
        Raw image bytes (PNG or JPEG)
    """
    # 1. Try Imagen 3
    image_bytes = _imagen3_generate(prompt, size)
    if image_bytes:
        return image_bytes

    # 2. Fall back to DALL-E 3
    image_bytes = _dalle3_generate(prompt, size)
    if image_bytes:
        return image_bytes

    raise RuntimeError(
        "Both Imagen 3 and DALL-E 3 failed to generate an image. "
        "Check GOOGLE_PROJECT_ID and OPENAI_API_KEY environment variables."
    )
