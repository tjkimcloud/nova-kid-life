"""
S3 uploader — stores all image variants with proper cache headers and CDN paths.

Path convention:
  events/{event_slug}/hero.webp
  events/{event_slug}/hero-md.webp
  events/{event_slug}/hero-sm.webp
  events/{event_slug}/card.webp
  events/{event_slug}/og.webp
  events/{event_slug}/social.webp

Cache strategy:
  - Images are content-addressed via event slug + filename
  - Cache-Control: public, max-age=31536000, immutable (1 year)
  - CloudFront serves from MEDIA_CDN_URL
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

_BUCKET   = os.getenv("MEDIA_BUCKET_NAME", "novakidlife-media")
_CDN_URL  = os.getenv("MEDIA_CDN_URL", "https://media.novakidlife.com").rstrip("/")
_REGION   = os.getenv("AWS_REGION", "us-east-1")

_s3_client = None


def _s3() -> boto3.client:
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3", region_name=_REGION)
    return _s3_client


# ── Upload helpers ─────────────────────────────────────────────────────────────

def _upload(key: str, data: bytes, content_type: str = "image/webp") -> str:
    """Upload bytes to S3 and return the CDN URL."""
    _s3().put_object(
        Bucket=_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
        CacheControl="public, max-age=31536000, immutable",
        # ACL is NOT set — bucket policy handles public read via CloudFront OAI
    )
    return f"{_CDN_URL}/{key}"


# ── Public API ─────────────────────────────────────────────────────────────────

@dataclass
class UploadedUrls:
    hero:    str = ""
    hero_md: str = ""
    hero_sm: str = ""
    card:    str = ""
    og:      str = ""
    social:  str = ""


def upload_all(
    event_slug: str,
    hero:    bytes,
    hero_md: bytes,
    hero_sm: bytes,
    card:    bytes,
    og:      bytes,
    social:  bytes,
) -> UploadedUrls:
    """
    Upload all image variants to S3 and return their CDN URLs.

    Args:
        event_slug: URL-safe event identifier (e.g. "fairfax-storytime-2026-03-20")
        hero … social: WebP bytes for each variant

    Returns:
        UploadedUrls with all CDN paths filled in
    """
    prefix = f"events/{event_slug}"

    return UploadedUrls(
        hero    = _upload(f"{prefix}/hero.webp",    hero),
        hero_md = _upload(f"{prefix}/hero-md.webp", hero_md),
        hero_sm = _upload(f"{prefix}/hero-sm.webp", hero_sm),
        card    = _upload(f"{prefix}/card.webp",    card),
        og      = _upload(f"{prefix}/og.webp",      og),
        social  = _upload(f"{prefix}/social.webp",  social),
    )


def image_already_exists(event_slug: str) -> bool:
    """Return True if the hero image already exists in S3 (skip re-generation)."""
    try:
        _s3().head_object(Bucket=_BUCKET, Key=f"events/{event_slug}/hero.webp")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise
