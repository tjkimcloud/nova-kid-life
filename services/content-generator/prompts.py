"""
Blog post generation prompts for content-generator Lambda.
All prompts target the NovaKidLife blog voice defined in skills/brand-voice.md.
"""
from __future__ import annotations

from datetime import date

# ── Shared voice instructions injected into every prompt ──────────────────────

_VOICE_RULES = """
VOICE:
- Second person ("you", "your kids", "your family") — never first-person singular
- Contractions always: "it's", "you'll", "don't", "there's"
- Em dashes (—) for natural asides: "Free to attend — no registration needed."
- Vary sentence length: mix short punchy sentences with longer descriptive ones
- Specific over vague: "about 25 minutes from Ashburn" not "conveniently located"
- Oxford comma always

NEVER WRITE:
- "Furthermore", "Additionally", "Moreover", "It's worth noting"
- "Fun-filled", "the whole family will love", "make memories", "exciting opportunity"
- "Families can enjoy", "needless to say", "in conclusion", "to summarize"
- "Fun options for your kids", "keep your little ones entertained", "of all ages", "fun for the whole family"
- "Don't miss out", "here's what the week has", "planning-mode energy"
- Three adjectives in a row
- Consecutive exclamation points — one per entire post maximum
- Never open with a meta-description of the tone or the post type

STRUCTURE PER EVENT (use exactly this format):
**[Event Name]** — [City, VA]
📅 [Day], [Month Date] · [Time]
📍 [Venue Name]
💰 [Free to attend / $X per person]

[3–5 sentence blurb: what + who → logistics detail → one insider tip if known → optional specific enthusiasm]

[→ Details](https://novakidlife.com/events/[slug])

INSIDER TIPS: Only include if genuinely specific and useful (parking, crowd timing,
registration deadline, age nuance). Skip this line entirely if not certain — never fabricate.
"""

_FAQ_INSTRUCTIONS = """
End every post with a ## Frequently Asked Questions section.
Write 3–4 questions exactly as a parent would type them into Google or ask an LLM.
Rules for good FAQ:
- Questions must be specific enough to be useful — not "What events are happening?" but "What free outdoor events are near Reston this weekend?"
- Answers must add information beyond what's already in the post — don't just repeat the event list
- Each answer should be 1–3 sentences, direct, and include at least one specific name/date/location
- Vary the question types: mix what/where/when/registration/cost questions
- Do NOT fabricate details — only answer what you know from the events data
Format:
**Q: [question]**
[answer]
"""


# ── Weekend roundup ────────────────────────────────────────────────────────────

def build_weekend_prompt(
    events: list[dict],
    start: date,
    end: date,
    area_label: str = "Northern Virginia",
) -> str:
    start_fmt = f"{start.strftime('%B')} {start.day}"
    end_fmt   = f"{end.day}, {end.year}"
    date_range = f"{start_fmt}–{end_fmt}"
    event_list = _format_event_list(events)

    return f"""You are writing a weekend roundup blog post for NovaKidLife, a family events site
for parents in {area_label}.

{_VOICE_RULES}

HOOK (2–3 sentences max):
Lead with something concrete and specific to this weekend — the weather, a standout event, the time of year.
Help the parent picture what kind of weekend is ahead based on the actual events below.
Do NOT start with "Here are the top events", "What an amazing weekend", or any generic opener.
Do NOT open with a question directed at the reader.

POST TITLE (H1): Things To Do With Kids in {area_label} This Weekend — {date_range}

BODY STRUCTURE:
- Group events by: ## Free Events | ## [Area/County] | ## Indoor Options (if rainy/winter)
- Bold each event name
- Use the logistics block format (📅 📍 💰) for every event
- Add H2 headers every 4–6 events
- Include "Jump to:" anchor nav at the top if more than 8 events

CLOSING LINE:
One sentence: "See every event happening this weekend at [novakidlife.com/events](https://novakidlife.com/events)."

{_FAQ_INSTRUCTIONS}
FAQ questions should be:
1. "What free events are happening in {area_label} this weekend?"
2. "What's happening in [specific city from events] this weekend for kids?"
3. "What indoor activities are available for kids in {area_label} this weekend?"
4. "Do I need to register in advance for weekend family events in {area_label}?"

OUTPUT FORMAT — return valid JSON only, no markdown wrapper:
{{
  "title": "Things To Do With Kids in {area_label} This Weekend — {date_range}",
  "meta_description": "[date range] · [N]+ family events across {area_label}. [2 specific highlights]. [Free/cost note].",
  "content": "[full markdown content]"
}}

Meta description must be 140–155 characters. Count carefully.

EVENTS (use ALL of these — do not skip any):
{event_list}
"""


# ── Location-specific roundup ──────────────────────────────────────────────────

def build_location_prompt(
    events: list[dict],
    start: date,
    end: date,
    area_label: str,
    county_label: str,
) -> str:
    start_fmt  = f"{start.strftime('%B')} {start.day}"
    end_fmt    = f"{end.day}, {end.year}"
    date_range = f"{start_fmt}–{end_fmt}"
    event_list = _format_event_list(events)

    return f"""You are writing a location-specific weekend roundup for NovaKidLife.
Target area: {area_label} ({county_label}).

{_VOICE_RULES}

HOOK (2–3 sentences):
Hyperlocal feel — write like someone who lives in {area_label}, not a visitor.
Mention something specific about {area_label} if relevant (the area, the season, a local landmark).

POST TITLE (H1): Things To Do With Kids in {area_label} This Weekend — {date_range}

BODY STRUCTURE:
- Organize by day (## Saturday, [Month Date] | ## Sunday, [Month Date]) or by neighborhood if events span multiple cities
- Bold each event name, use the logistics block format
- Include insider local tips — parking, crowd timing, registration deadlines

CLOSING LINE:
"See all {area_label} family events at [novakidlife.com/events](https://novakidlife.com/events?location={area_label.lower().replace(' ', '-')})."

{_FAQ_INSTRUCTIONS}
FAQ questions should be hyperlocal to {area_label}:
1. "What's happening in {area_label} this weekend for kids?"
2. "What free events are in {area_label} this weekend?"
3. "What are the best family activities in {area_label} on [Saturday date]?"
4. "Are there any indoor kids activities in {area_label} this weekend?"

OUTPUT FORMAT — return valid JSON only:
{{
  "title": "Things To Do With Kids in {area_label} This Weekend — {date_range}",
  "meta_description": "[date range] · Family events in {area_label}. [2 specific highlights]. [Free/cost note].",
  "content": "[full markdown content]"
}}

EVENTS:
{event_list}
"""


# ── Free events roundup ────────────────────────────────────────────────────────

def build_free_events_prompt(
    events: list[dict],
    start: date,
    end: date,
    area_label: str = "Northern Virginia",
) -> str:
    start_fmt  = f"{start.strftime('%B')} {start.day}"
    end_fmt    = f"{end.day}, {end.year}"
    date_range = f"{start_fmt}–{end_fmt}"
    event_list = _format_event_list(events)

    return f"""You are writing a "free things to do this weekend" roundup for NovaKidLife.
All events in this post are free or free to attend (may have optional paid components).

{_VOICE_RULES}

HOOK (2–3 sentences):
Lead with the value proposition — this is genuinely useful for budget-conscious families.
Tone: practical and a little enthusiastic about the value, not preachy.

POST TITLE (H1): Free Things To Do With Kids in {area_label} This Weekend — {date_range}

BODY STRUCTURE:
- Group by: ## Free Outdoor Activities | ## Free Indoor Events | ## Free Library Programs | ## Free Community Events
- For each event, clearly state "Free to attend" in the 💰 line
- Note any "free but registration required" events — important distinction for parents

CLOSING LINE:
"More free events at [novakidlife.com/events](https://novakidlife.com/events?is_free=true)."

{_FAQ_INSTRUCTIONS}
FAQ questions:
1. "What free things can I do with kids in {area_label} this weekend?"
2. "Are there any free outdoor activities for kids in {area_label} this weekend?"
3. "What free library events are happening in {area_label} this weekend?"
4. "What free kids activities don't require registration in {area_label} this weekend?"

OUTPUT FORMAT — return valid JSON only:
{{
  "title": "Free Things To Do With Kids in {area_label} This Weekend — {date_range}",
  "meta_description": "[date range] · [N]+ free family events in {area_label}. [2 specific highlights]. No cost to attend.",
  "content": "[full markdown content]"
}}

EVENTS (all free to attend):
{event_list}
"""


# ── Week-ahead roundup ─────────────────────────────────────────────────────────

def build_week_ahead_prompt(
    events: list[dict],
    start: date,
    end: date,
    area_label: str = "Northern Virginia",
) -> str:
    start_fmt  = f"{start.strftime('%B')} {start.day}"
    end_fmt    = f"{end.day}, {end.year}"
    date_range = f"{start_fmt}–{end_fmt}"
    event_list = _format_event_list(events)

    return f"""You are writing a week-ahead family events guide for NovaKidLife.
This goes out Monday morning to help parents plan the week in {area_label}.

{_VOICE_RULES}

HOOK (2–3 sentences):
Open with something concrete and specific — name the week, the standout event, or a time-sensitive deadline.
Tone is practical and helpful, like a knowledgeable neighbor texting you a heads-up.
Do NOT write a meta-commentary about planning or Monday. Just get into the week.
Highlight the 1–2 most time-sensitive events (registration deadlines, limited spots) by name.

POST TITLE (H1): Family Events in {area_label} This Week — {date_range}

BODY STRUCTURE:
- Organize by day: ## Monday | ## Tuesday | etc. (skip days with no events)
- Include weekday events that parents might miss (after-school programs, weeknight storytime, etc.)
- Flag registration deadlines prominently

CLOSING LINE:
"Full calendar at [novakidlife.com/events](https://novakidlife.com/events)."

{_FAQ_INSTRUCTIONS}
FAQ questions:
1. "What family events are happening this week in {area_label}?"
2. "What kids activities are available on weeknights in {area_label} this week?"
3. "Are there any events this week in {area_label} that require advance registration?"
4. "What's the best family event in {area_label} this week?"

OUTPUT FORMAT — return valid JSON only:
{{
  "title": "Family Events in {area_label} This Week — {date_range}",
  "meta_description": "[date range] · [N]+ family events across {area_label} this week. [2 highlights]. Register early for some.",
  "content": "[full markdown content]"
}}

EVENTS:
{event_list}
"""


# ── Indoor / rainy day roundup ─────────────────────────────────────────────────

def build_indoor_prompt(
    events: list[dict],
    start: date,
    end: date,
    area_label: str = "Northern Virginia",
) -> str:
    start_fmt  = f"{start.strftime('%B')} {start.day}"
    end_fmt    = f"{end.day}, {end.year}"
    date_range = f"{start_fmt}–{end_fmt}"
    event_list = _format_event_list(events)

    return f"""You are writing an indoor / rainy day activities guide for NovaKidLife.
All events in this post are indoors or weather-independent.

{_VOICE_RULES}

HOOK (2–3 sentences):
Problem-solving energy — "we've got you covered." Acknowledge the rainy/cold day context.
Don't be dramatic about rain. Just: here's what to do.

POST TITLE (H1): Indoor Activities for Kids in {area_label} This Weekend — {date_range}

BODY STRUCTURE:
- Group by: ## Museums & Learning | ## Active Indoor Fun | ## Performances & Shows | ## Library Programs
- Note which require advance booking — parents hate showing up to a sold-out event

CLOSING LINE:
"Browse all indoor and year-round events at [novakidlife.com/events](https://novakidlife.com/events)."

{_FAQ_INSTRUCTIONS}
FAQ questions:
1. "What indoor activities are available for kids in {area_label} this weekend?"
2. "What can I do with kids on a rainy day in {area_label}?"
3. "What indoor family events are free in {area_label} this weekend?"
4. "What are the best indoor kids activities near me in Northern Virginia?"

OUTPUT FORMAT — return valid JSON only:
{{
  "title": "Indoor Activities for Kids in {area_label} This Weekend — {date_range}",
  "meta_description": "[date range] · [N]+ indoor family activities in {area_label}. [2 highlights]. Rain-proof weekend plans.",
  "content": "[full markdown content]"
}}

EVENTS:
{event_list}
"""


# ── Seasonal roundup ───────────────────────────────────────────────────────────

def build_seasonal_prompt(
    events: list[dict],
    start: date,
    end: date,
    area_label: str,
    season_name: str,
    focus_keywords: list[str],
    seo_title: str,
) -> str:
    start_fmt  = f"{start.strftime('%B')} {start.day}"
    end_fmt    = f"{end.day}, {end.year}"
    date_range = f"{start_fmt}–{end_fmt}"
    event_list = _format_event_list(events)
    keywords   = ", ".join(focus_keywords)

    return f"""You are writing a seasonal family events guide for NovaKidLife.
Season/theme: {season_name}
Target area: {area_label}
Focus keywords to weave in naturally (do NOT keyword-stuff): {keywords}

{_VOICE_RULES}

HOOK (2–3 sentences):
Lead with the seasonal moment — what makes this time of year special in {area_label}.
Be specific: cherry blossoms at peak, Easter weekend countdown, spring break starting, etc.
Make parents feel like they're getting insider knowledge, not a press release.

POST TITLE (H1): {seo_title}

BODY STRUCTURE:
- Open with a short intro paragraph (3–4 sentences) about why this season is worth getting out for
- Group events into relevant H2 sections (e.g. ## Cherry Blossom Events | ## Easter Egg Hunts | ## Free Outdoor Activities | ## Spring Break Day Trips)
- Use the logistics block format (📅 📍 💰) for every event
- For seasonal events, include any time-sensitive notes (peak bloom window, sold-out risk, registration deadline)
- Skip events that have no seasonal connection — it's fine to feature 5 great ones over 12 mediocre ones

INSIDER ANGLE:
Include 2–3 details that only a NoVa local would know — best viewing spots, crowd timing,
parking tips, which locations are most family-friendly for this season.
Example: "The Tidal Basin crowds peak around 10am — if you're coming from NoVa, aim for the 7–8am
opening or plan for a late-afternoon visit after 3pm when tour buses leave."

CLOSING LINE:
One sentence linking to the relevant events section: "See all spring events at [novakidlife.com/events](https://novakidlife.com/events)."

{_FAQ_INSTRUCTIONS}
FAQ questions must target how parents actually search for this season:
1. "{focus_keywords[0]} Northern Virginia {start.year}" style question
2. "Free {season_name.lower()} activities kids {area_label}"
3. Best time / best spot type question specific to the season
4. "Do I need to register" or logistics question for the top event type

OUTPUT FORMAT — return valid JSON only:
{{
  "title": "{seo_title}",
  "meta_description": "[season highlight] · [N]+ {season_name.lower()} events in {area_label}. [2 specific highlights with dates/locations].",
  "content": "[full markdown content]"
}}

Meta description must be 140–155 characters. Count carefully.

EVENTS (feature the most seasonally relevant — you may skip events with no seasonal tie):
{event_list}
"""


# ── Helper ─────────────────────────────────────────────────────────────────────

def _format_event_list(events: list[dict]) -> str:
    """Format events as a numbered list for GPT context."""
    lines = []
    for i, e in enumerate(events, 1):
        cost = "Free to attend" if e.get("is_free") else (e.get("cost_description") or "Check event page")
        start = e.get("start_at", "")[:16].replace("T", " ") if e.get("start_at") else "TBD"
        lines.append(
            f"{i}. {e.get('title', 'Untitled')}\n"
            f"   Slug: {e.get('slug', '')}\n"
            f"   Venue: {e.get('venue_name', '')} — {e.get('location_text', '')}\n"
            f"   Start: {start}\n"
            f"   Cost: {cost}\n"
            f"   Tags: {', '.join(e.get('tags') or [])}\n"
            f"   Description: {(e.get('short_description') or '')[:200]}"
        )
    return "\n\n".join(lines)
