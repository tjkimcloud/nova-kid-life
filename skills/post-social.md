# Skill: Post to Social Media (Buffer API)

**Purpose:** Schedule and publish event posts to social media channels via Buffer.

## Prerequisites
- `BUFFER_ACCESS_TOKEN` in SSM at `/novakidlife/buffer/access-token`
- Buffer channels configured (Facebook, Instagram, Twitter/X)
- Event has `image_url`, `title`, `short_description` populated

## Service: `services/social-poster/`

## Buffer API Client

```python
import httpx

BUFFER_API_BASE = "https://api.bufferapp.com/1"

class BufferClient:
    def __init__(self, access_token: str):
        self.token = access_token
        self.client = httpx.Client(
            base_url=BUFFER_API_BASE,
            timeout=30,
        )

    def get_profiles(self) -> list[dict]:
        resp = self.client.get(
            "/profiles.json",
            params={"access_token": self.token},
        )
        resp.raise_for_status()
        return resp.json()

    def create_post(
        self,
        profile_ids: list[str],
        text: str,
        media_url: str | None = None,
        scheduled_at: str | None = None,
    ) -> dict:
        payload = {
            "access_token": self.token,
            "profile_ids[]": profile_ids,
            "text": text,
        }
        if media_url:
            payload["media[photo]"] = media_url
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at  # ISO 8601

        resp = self.client.post("/updates/create.json", data=payload)
        resp.raise_for_status()
        return resp.json()
```

## Post Copy Templates

```python
def build_post_copy(event: dict) -> str:
    """Generate social post copy from event data."""
    hashtags = " ".join(f"#{tag}" for tag in event.get("tags", [])[:4])
    return (
        f"🎉 {event['title']}\n\n"
        f"{event['short_description']}\n\n"
        f"📅 {event['date_formatted']}\n"
        f"📍 {event['location']}\n\n"
        f"Full details → novakidlife.com/events/{event['slug']}\n\n"
        f"{hashtags} #NoVaKids #NorthernVirginia #FamilyFun"
    )
```

## Lambda Handler

```python
def handler(event, context):
    for record in event["Records"]:  # SQS trigger
        body = json.loads(record["body"])
        event_data = body["event"]

        token = get_ssm_parameter("/novakidlife/buffer/access-token")
        client = BufferClient(token)

        profiles = get_ssm_parameter("/novakidlife/buffer/profile-ids")
        profile_ids = profiles.split(",")

        text = build_post_copy(event_data)

        result = client.create_post(
            profile_ids=profile_ids,
            text=text,
            media_url=event_data.get("image_url"),
            # Schedule for next 9am-5pm window:
            scheduled_at=next_optimal_posting_time(),
        )

        logger.info("Queued post %s for event %s", result["id"], event_data["id"])
```

## Optimal Posting Times
- Weekdays: 9am, 12pm, 5pm EST
- Weekends: 10am, 2pm EST
- Avoid: 11pm–7am

## Verify
```bash
# Check Buffer queue via API
curl "https://api.bufferapp.com/1/profiles/<id>/updates/pending.json?access_token=<token>"
```

## Rate Limits
- Buffer free: 10 scheduled posts/profile
- Buffer Essentials: 100 posts/profile
- Throttle: max 1 post per event per platform
