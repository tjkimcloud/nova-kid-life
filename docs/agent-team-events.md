# Agent Team: Event Discovery Pipeline

**Document type:** Architecture design (not yet implemented)
**Slash command:** `/discover-events`
**Trigger:** Manual or EventBridge daily 6am EST

---

## The Problem This Architecture Solves

Event sources fall into two fundamentally different categories:

| Category | Characteristic | Example sources |
|----------|---------------|-----------------|
| **Region-specific** | Already scoped to one county/city | Fairfax County Library, Loudoun County Parks, Arlington Recreation |
| **Aggregate** | Mix events from all of NoVa with no regional grouping | dullesmoms.com, Eventbrite NoVA, Meetup, Patch.com, Facebook groups, Nextdoor |

Region-specific sources → sub-agents can populate `city` and `county` at scrape time.
Aggregate sources → sub-agents must preserve raw location strings; Team Leader classifies after ingestion.

Forcing aggregate sources into a regional structure they don't have creates false data. This architecture handles both types correctly.

---

## Team Structure

```
/discover-events
    │
    ▼
Team Leader (Opus 4)
    ├── assigns Tier 1 agents (9 region-specific sources)
    ├── assigns Tier 2 agents (6 aggregate sources)
    ├── waits for all agents to complete
    ├── runs regional classification on Tier 2 events
    ├── runs deduplication across all events
    ├── runs age/category tagging
    ├── writes final events to Supabase
    └── appends run summary to memory.md
         │
         ├── Tier 1 Sub-Agents (Sonnet × 9) — region-specific
         │     Each scrapes one source, returns normalized events
         │     with city + county already populated
         │
         └── Tier 2 Sub-Agents (Sonnet × 6) — aggregate
               Each scrapes one source, returns ALL events found
               with city = null, county = null
               location_raw preserved exactly as scraped
```

---

## Normalized Event Object Schema

Every sub-agent (both tiers) returns events in this exact shape. No exceptions.

```json
{
  "source_url":       "string — canonical URL of the individual event page",
  "source_name":      "string — human-readable source name (e.g. 'Fairfax County Library')",
  "title":            "string",
  "description":      "string",
  "start_date":       "ISO 8601 — e.g. 2026-03-21T10:00:00-04:00",
  "end_date":         "ISO 8601 or null",
  "location_raw":     "string — EXACT location text as scraped, NEVER modified",
  "location_name":    "string — venue name if identifiable, else null",
  "city":             "string — Tier 1: populated by agent. Tier 2: null",
  "county":           "string — Tier 1: populated by agent. Tier 2: null",
  "cost":             "string — e.g. 'Free', '$5/person', 'Free with admission'",
  "registration_url": "string or null",
  "age_range":        "string or null — e.g. 'Ages 2–6', 'All ages'",
  "scraped_at":       "ISO 8601 — time this agent ran"
}
```

**Critical rule:** `location_raw` is immutable once set by a sub-agent. The Team Leader reads it but never writes to it.

---

## Tier 1 — Region-Specific Source Agents (Sonnet)

One agent per source. Each receives a specific URL or URL list, scrapes, normalizes, and returns events with `city` and `county` already populated — the source tells us the region.

| Agent | Source | county | city (populated) |
|-------|--------|--------|-----------------|
| `agent-fairfax-library` | Fairfax County Library system (all branches) | Fairfax | Per-branch city |
| `agent-loudoun-library` | Loudoun County Library | Loudoun | Per-branch city |
| `agent-arlington-library` | Arlington Public Library | Arlington | Arlington |
| `agent-pw-library` | Prince William Library system | Prince William | Per-branch city |
| `agent-fairfax-parks` | Fairfax County Parks & Rec | Fairfax | Per-facility city |
| `agent-loudoun-parks` | Loudoun County Parks & Rec | Loudoun | Per-facility city |
| `agent-nova-parks` | NOVA Parks (regional parks authority) | varies | Per-park city |
| `agent-reston-cc` | Reston Community Center | Fairfax | Reston |
| `agent-arlington-rec` | Arlington Recreation programs | Arlington | Arlington |

---

## Tier 2 — Aggregate Source Agents (Sonnet)

One agent per source. Each scrapes the full source without regional filtering and returns ALL events with `city = null`, `county = null`. The Team Leader classifies location after ingestion.

| Agent | Source | Why aggregate |
|-------|--------|---------------|
| `agent-dullesmoms` | dullesmoms.com | Covers all of NoVa + DC suburbs |
| `agent-eventbrite` | Eventbrite (NoVA search) | Events from all counties mixed together |
| `agent-meetup` | Meetup (NoVA search) | Events from all counties mixed together |
| `agent-patch` | Patch.com (all NoVA editions) | Multi-edition — no per-county API |
| `agent-facebook-groups` | Facebook community groups (NoVa parent groups) | Cross-regional community posts |
| `agent-nextdoor` | Nextdoor local posts (NoVa neighborhoods) | Neighborhood-level, no county structure |

**Mandatory rule for all Tier 2 agents:**
> Do NOT attempt to normalize or classify location. Preserve `location_raw` exactly as scraped. Set `city = null` and `county = null`. The Team Leader owns classification.

---

## Team Leader Responsibilities (Opus 4)

### 1. Task Assignment & Race Condition Prevention

- Maintain a master source list with `status`: `unassigned | in_progress | complete | failed`
- Never assign the same source to two agents simultaneously
- If an agent fails: mark source as `failed`, log the error, continue with remaining sources (do not block the run)

### 2. Regional Classification (Tier 2 events only)

After receiving events from aggregate agents, classify `city` and `county` using this logic **in order**:

```
1. Parse location_raw for known NoVa city names:
   Reston, Herndon, Chantilly, McLean, Vienna, Burke, Springfield, Centreville,
   Annandale, Falls Church, Leesburg, Ashburn, Sterling, Purcellville, Broadlands,
   Lansdowne, Arlington, Clarendon, Ballston, Shirlington, Alexandria,
   Manassas, Woodbridge, Dale City, Gainesville, Haymarket, Lake Ridge

2. Parse location_raw for NoVa zip codes → map to county:
   20xxx (Fairfax range), 201xx (Loudoun range), 222xx (Arlington), 20xxx (Prince William)
   [Use the zip-to-county reference table in memory.md]

3. Parse location_raw for known venue names:
   "Reston Town Center" → Reston / Fairfax
   "One Loudoun" → Ashburn / Loudoun
   "Mosaic District" → Fairfax / Fairfax
   "Dulles Town Center" → Sterling / Loudoun
   [Full venue mapping to be maintained in memory.md]

4. If none of the above resolve:
   Set county = "unclassified", city = "unclassified"
   Log to memory.md under "unclassified_events"
   DO NOT discard — store in Supabase with unclassified flag
```

### 3. Deduplication

An event is a duplicate if **two or more** of these match across events from different sources:

| Signal | Matching method |
|--------|----------------|
| `title` | Fuzzy match ≥ 85% similarity (use Levenshtein or similar) |
| `start_date` | Exact ISO date match (ignore time if one source lacks it) |
| `location_name` or `location_raw` | Fuzzy match ≥ 80% |

**When a duplicate is detected:**
1. Keep the event with the most complete field set (most non-null fields wins)
2. Merge `source_url` from both records into a `source_urls: string[]` array
3. Discard the thinner record
4. Increment `duplicates_removed` counter in the run log

### 4. Age/Category Tagging

After classification and deduplication, run tag assignment on all events:
- Age range normalization: "toddlers" → "ages 1–3", "kids" → "ages 3–12", "teens" → "ages 13–17"
- Category tags: library, outdoor, arts-crafts, sports, educational, music, nature, holiday, food, deal, pokemon

### 5. Database Write

Upsert all final events to Supabase `events` table using `ON CONFLICT (source_url)` for idempotency.
If an event has `source_urls[]` (merged duplicate), use the primary source URL as the `source_url` key.

### 6. Run Summary

After all agents complete, append to `memory.md`:
```
## Discover Events Run — [ISO timestamp]
- Total events found: [N] (across all agents)
- Tier 1 events: [N]
- Tier 2 events: [N] (before classification)
- Unclassified events: [N] (logged separately below)
- Duplicates removed: [N]
- Events written to DB: [N]
- Failed sources: [list, if any]
- Agent errors: [list, if any]
```

---

## Shared memory.md Schema

Each sub-agent appends one entry on completion. Team Leader appends the final summary.

```yaml
agent_name:         "agent-fairfax-library"     # which agent wrote this
source_url:         "https://..."               # what was scraped
events_found:       42                          # count of raw events returned
errors:             []                          # scrape failures or parsing errors
timestamp:          "2026-03-21T06:15:00-04:00" # ISO 8601

# Team Leader only:
unclassified_events: 3                          # events that couldn't be classified
duplicates_removed:  7                          # duplicates detected and merged
events_written_to_db: 156                       # final count written
```

---

## Slash Command: `/discover-events`

When triggered:

1. Team Leader initializes, builds master source list with `status = unassigned`
2. Assigns all Tier 1 agents their source URLs — they run in parallel
3. Assigns all Tier 2 agents their source URLs — they run in parallel with Tier 1
4. Team Leader waits for all agents (does not proceed until all complete or time out after 10 min)
5. Runs regional classification on all Tier 2 events
6. Runs deduplication across all events
7. Runs age/category tagging
8. Writes final event set to Supabase
9. Appends run summary to `memory.md`
10. Returns: total events written, any failures, unclassified count

**Failure handling:**
- If a Tier 1 or Tier 2 agent times out (> 5 min): mark source as `failed`, continue
- If Supabase write fails: retry up to 3 times with exponential backoff; if still failing, log and halt
- Never silently discard events — every failure gets logged with the original event payload

---

## Implementation Notes (for future Session 14)

- **Model selection:** Team Leader uses Opus 4 for classification judgment calls. Sub-agents use Sonnet for cost efficiency.
- **Facebook + Nextdoor agents** will require the human-in-the-loop scraping approach discussed in `project_facebook_nextdoor.md` memory entry — these cannot be automated headlessly at launch. Include in design but mark as `manual_trigger_required` until that approach is built.
- **Rate limiting:** Tier 2 aggregate sources (Eventbrite, Meetup) have API rate limits — sub-agents must include backoff logic.
- **Existing scraper relationship:** This agent team design eventually replaces the current `events-scraper` Lambda for Tier 1/2 sources. The Tier 3 deal monitor and Pokémon scrapers are out of scope for this agent team — they remain as Lambda functions.
