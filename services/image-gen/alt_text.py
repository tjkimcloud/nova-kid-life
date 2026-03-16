"""
AI-generated alt text for SEO and accessibility.

Produces concise, keyword-rich alt text (< 125 chars) that describes the image
in context of the event — better for screen readers and Google image search.
"""
from __future__ import annotations

import os
from openai import OpenAI

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def generate_alt_text(event: dict) -> str:
    """
    Generate SEO alt text for an event image.

    Args:
        event: Event dict with at minimum: title, location_name,
               event_type, tags, and optionally description

    Returns:
        Alt text string (≤ 125 characters)
    """
    title         = event.get("title", "Family event")
    location      = event.get("location_name", "Northern Virginia")
    event_type    = event.get("event_type", "event")
    tags          = ", ".join(event.get("tags", [])[:5])
    description   = (event.get("description") or "")[:300]

    system_prompt = (
        "You write concise, descriptive image alt text for a family events website. "
        "Alt text must: (1) describe what is visually shown, (2) include the event name "
        "and location naturally, (3) be under 125 characters, (4) avoid starting with "
        "'Image of' or 'Photo of', (5) be suitable for screen readers and Google image search."
    )

    user_prompt = (
        f"Write alt text for an image of this event:\n"
        f"Title: {title}\n"
        f"Location: {location}\n"
        f"Type: {event_type}\n"
        f"Tags: {tags}\n"
        f"Description excerpt: {description}\n\n"
        f"Output only the alt text, nothing else."
    )

    try:
        response = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=60,
            temperature=0.3,
        )
        alt = response.choices[0].message.content.strip()

        # Enforce 125-char limit (truncate at word boundary)
        if len(alt) > 125:
            alt = alt[:122].rsplit(" ", 1)[0] + "..."

        return alt

    except Exception:
        # Fallback: construct alt text from event metadata
        return _fallback_alt(title, location, event_type)


def _fallback_alt(title: str, location: str, event_type: str) -> str:
    """Simple deterministic alt text when the AI call fails."""
    base = f"{title} at {location}"
    if len(base) <= 125:
        return base
    return f"{title[:80]}... in Northern Virginia"
