# Skill: Generate Event Content (AI)

**Purpose:** Use gpt-4o-mini to generate structured event data for NovaKidLife.

## Prerequisites
- `OPENAI_API_KEY` set in environment
- Supabase client configured

## Python: Generate Single Event

```python
import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """You are a family events copywriter for NovaKidLife,
a Northern Virginia family events platform.
Write engaging, accurate event descriptions for parents with young children.
Always respond with valid JSON matching the schema provided."""

def generate_event(raw_event_data: dict) -> dict:
    """Generate enriched event content from raw scraped data."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"""Generate event content for:
{json.dumps(raw_event_data, indent=2)}

Return JSON with these fields:
{{
  "title": "engaging event title (max 60 chars)",
  "short_description": "1-2 sentence hook for parents (max 120 chars)",
  "full_description": "3-4 paragraph event description, family-focused",
  "age_range": "e.g. '2-8 years' or 'All ages'",
  "tags": ["array", "of", "relevant", "tags"],
  "seo_title": "SEO-optimized title (max 60 chars)",
  "seo_description": "Meta description (max 155 chars)"
}}"""
            }
        ],
        max_tokens=800,
        temperature=0.7,
    )

    return json.loads(response.choices[0].message.content)
```

## Batch Generation

```python
import asyncio
from openai import AsyncOpenAI

async_client = AsyncOpenAI()

async def generate_events_batch(raw_events: list[dict]) -> list[dict]:
    tasks = [generate_event_async(e) for e in raw_events]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

## Cost Estimate
- gpt-4o-mini: ~$0.00015/1K input tokens, ~$0.0006/1K output tokens
- ~800 tokens per event → ~$0.001 per event
- 100 events/day → ~$0.10/day

## Output Validation

Always validate the generated JSON against your Pydantic model before inserting:
```python
from pydantic import BaseModel

class EventContent(BaseModel):
    title: str
    short_description: str
    full_description: str
    age_range: str
    tags: list[str]
    seo_title: str
    seo_description: str

def validate_generated_event(raw: dict) -> EventContent:
    return EventContent(**raw)
```

## Error Handling
- Catch `json.JSONDecodeError` — retry once with explicit JSON reminder
- Catch `openai.RateLimitError` — exponential backoff
- Log failures to CloudWatch and continue batch (don't fail entire run)
