# Skill: MCP Builder — NovaKidLife

**Purpose:** Guide for designing and building Model Context Protocol (MCP) servers that extend Claude's capabilities with NovaKidLife-specific tools. Use when building future MCP integrations for the platform.

Reference: MCP protocol spec at `https://modelcontextprotocol.io/llms-full.txt`

---

## What is an MCP (in this context)

An MCP server lets Claude directly interact with NovaKidLife systems — querying events, triggering scrapes, managing posts — without going through the web UI. It turns Claude into an operations agent for the platform.

Think of it as: **Claude Code + MCP = Claude can operate NovaKidLife directly.**

---

## Planned NovaKidLife MCPs

### 1. `novakidlife-events` MCP (highest priority)
Enables Claude to answer live event queries and manage the events database.

**Tools to build:**
```python
search_events(query: str, section: str, limit: int) → Event[]
# Semantic search via pgvector — "free events this weekend in Reston"

get_upcoming_events(days: int, section: str, is_free: bool) → Event[]
# Filter upcoming events for planning/reporting

get_event(slug: str) → Event
# Full event detail

publish_event(event_data: dict) → Event
# Insert a manually-curated event

archive_event(slug: str) → bool
# Archive stale or cancelled events

get_stats() → dict
# Total events, by section, by status, by event_type
```

**Use cases:**
- "What free events are happening in Fairfax this weekend?"
- "Show me all Pokémon events in the next 30 days"
- "Archive all events that ended more than 7 days ago"

### 2. `novakidlife-admin` MCP
Operational control of the platform.

**Tools to build:**
```python
trigger_scrape(tier: str = "all") → dict
# Invoke events-scraper Lambda

add_source(url: str, name: str, tier: int) → bool
# Add entry to config/sources.json

get_queue_depth() → dict
# Check SQS queue + DLQ depths

get_lambda_errors(hours: int = 24) → list
# Pull recent Lambda errors from CloudWatch

redrive_dlq(queue_name: str) → int
# Move DLQ messages back to main queue
```

### 3. `novakidlife-social` MCP
Manage social media content and Buffer queue.

**Tools to build:**
```python
get_pending_posts() → list
# See what's scheduled in Buffer

create_post(event_slug: str, platform: str) → dict
# Generate + schedule a post for a specific event

get_post_analytics(days: int) → dict
# Engagement metrics by platform
```

---

## Design Principles (from MCP Builder skill)

### Build for agent workflows, not API wrappers
- Each tool should complete a meaningful task, not just wrap one API call
- Return only high-signal data (omit raw embeddings, internal IDs)
- Include `concise` vs `detailed` response options where useful

### Error messages should guide next steps
```python
# Bad
raise ValueError("Event not found")

# Good
raise ValueError(f"Event '{slug}' not found. Try search_events('{slug[:10]}') to find similar events.")
```

### Tool annotations
```python
@mcp.tool(
    read_only_hint=True,      # search_events — safe to call freely
    destructive_hint=False,
    idempotent_hint=True,
)
```

---

## Implementation Stack

**Language:** Python (FastMCP)

```python
from fastmcp import FastMCP
from supabase import create_client

mcp = FastMCP("novakidlife-events")

@mcp.tool()
async def search_events(query: str, section: str = "main", limit: int = 10) -> list[dict]:
    """Search NovaKidLife events using semantic similarity.

    Args:
        query: Natural language query (e.g. "free storytime for toddlers in Fairfax")
        section: Site section - "main" for family events, "pokemon" for TCG events
        limit: Max results (1-20)

    Returns:
        List of matching events with title, date, location, cost, and event page URL
    """
    # 1. Generate embedding via OpenAI
    # 2. Call Supabase search_events() RPC
    # 3. Map DB columns → response fields
    # 4. Return concise event summaries
    ...
```

**Project structure:**
```
mcp-servers/
└── novakidlife-events/
    ├── server.py          # FastMCP server entry point
    ├── tools/
    │   ├── events.py      # search, get, publish, archive
    │   ├── admin.py       # scrape, queue, logs
    │   └── social.py      # buffer integration
    ├── db.py              # Supabase client (reuse from services/api/db.py)
    ├── requirements.txt
    └── README.md
```

---

## Development Process

### Phase 1: Plan
- Define exactly which tools are needed
- Map each tool to the API routes or DB operations it replaces
- Decide return shapes (what does Claude need to answer the question?)

### Phase 2: Build
1. Set up FastMCP boilerplate
2. Build shared DB client + error handling utilities
3. Implement tools one at a time, test each with Claude
4. Add proper docstrings (Claude reads these to decide when to use the tool)

### Phase 3: Test
Run MCP server locally, connect to Claude Code:
```json
// ~/.claude.json or mcp config
{
  "mcpServers": {
    "novakidlife-events": {
      "command": "python",
      "args": ["mcp-servers/novakidlife-events/server.py"],
      "env": {
        "SUPABASE_URL": "...",
        "SUPABASE_SERVICE_KEY": "..."
      }
    }
  }
}
```

### Phase 4: Evaluate
Generate 10 test questions with known answers:
```
Q: "How many published Pokémon events are there?"
A: [run get_stats() and verify count matches Supabase Studio]

Q: "What's the next free storytime at Fairfax Library?"
A: [run search_events("free storytime Fairfax Library") and verify result]
```

---

## When to Use MCP vs Lambda vs Skill

| Need | Use |
|------|-----|
| Claude needs to query/modify NovaKidLife data interactively | MCP |
| Automated background task (scheduled or event-triggered) | Lambda |
| Operational runbook / how-to guide for Claude | Skill |
| One-time data migration | Direct Supabase SQL |
