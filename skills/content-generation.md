# Skill: Content Generation — NovaKidLife

**Purpose:** Generate all types of content for NovaKidLife — event descriptions, social captions, email newsletters, weekly roundups, and GEO-optimized copy. Apply brand voice guidelines from `skills/brand-voice.md`. Apply SEO+GEO standards from `skills/seo-geo.md`.

---

## Content Types & Templates

### 1. Event Description (website — `full_description` field)

**Structure (answer-first per GEO spec):**
1. What is this event? (1 sentence, includes event type + audience)
2. When? (date + time)
3. Where? (venue + address + city)
4. Who is it for? (age range)
5. How much? (free/cost)
6. How to attend? (registration or walk-in)
7. Additional details (what to expect, what to bring)

**Template:**
```
{Event name} is a {event type} for {audience} at {venue} in {city}, Virginia.

Join us on {day}, {month} {date} from {start time} to {end time} for {brief description of what happens}.

{2–3 sentences of engaging descriptive detail — what kids/families will experience, see, do}

{Any requirements: registration, tickets, age restrictions, what to bring}

{Source attribution if applicable: "Sourced from Fairfax County Library" or "Via Eventbrite"}
```

**Example (150 words, answer-first):**
```
Fairfax County Library's Saturday Storytime is a free drop-in program for children ages 2–6 at the Chantilly Regional Library in Chantilly, Virginia.

Join us Saturday, March 21 at 10:00 AM for an interactive storytime session featuring picture books, songs, and movement activities designed to build early literacy skills.

Each session runs approximately 45 minutes and is led by a children's librarian. No tickets or advance registration required — families can simply arrive and enjoy. Seating is first-come, first-served and space may be limited.

Free to attend. Open to all Fairfax County residents and visitors.

Sourced from Fairfax County Public Library.
```

---

### 2. Short Description (API / card copy — `short_description` field, ≤120 chars)

**Formula:** `{What} for {who} at {location}. {Free/cost}.`

**Examples:**
- `Free drop-in storytime for ages 2–6 at Chantilly Library. No registration needed.`
- `Pokémon TCG league night at Nerd Rage Gaming, Manassas. $5 entry.`
- `Cox Farms fall festival — hayrides, pumpkins, animals. $20/person.`

---

### 3. SEO Meta Description (140–155 chars — see `skills/seo-geo.md`)

**Formula:** `{Day}, {Month Date} · {Time} at {Location}. {60-char snippet}. {Free/cost}.`

**Generation prompt for gpt-4o-mini:**
```python
PROMPT = """Write a meta description for this event page. Requirements:
- Exactly 140–155 characters (count carefully)
- Format: {Day}, {Month Date} · {Time} at {Location}. {snippet}. {cost}.
- Include the day of week, date, time, location name, and whether it's free
- End with cost or mild CTA
- No marketing fluff

Event: {title}
Date: {start_at}
Location: {venue_name}, {city}
Free: {is_free}
Cost: {cost_description}
Description: {full_description[:200]}
"""
```

---

### 4. FAQ Content (for JSON-LD + visible FAQ section)

Generate 4 Q&As per event. Rules:
- Questions use the exact event title
- Answers are factual, concise, 1–2 sentences
- Include location city in the "where" answer
- Include registration URL in "how to register" if exists

**Template:**
```python
def generate_faq(event):
    return [
        {
            "q": f"Is {event['title']} free?",
            "a": f"Yes, {event['title']} is free to attend." if event['is_free']
                 else f"{event['title']} costs {event['cost_description']}."
        },
        {
            "q": f"Where is {event['title']} held?",
            "a": f"{event['title']} is held at {event['venue_name']} in {city}, Virginia."
                 + (f" The address is {event['address']}." if event['address'] else "")
        },
        {
            "q": f"What age is {event['title']} for?",
            "a": age_range_sentence(event)
        },
        {
            "q": f"How do I register for {event['title']}?",
            "a": f"Register online at {event['registration_url']}." if event['registration_url']
                 else "No registration required — just show up."
        }
    ]
```

---

### 5. Social Captions by Platform

See `skills/social-strategy.md` for full templates. Quick reference:

**Twitter/X (max 280 chars):**
```
{Hook: event + date}
{Key details: location + cost + age}
{Link}
{2–3 hashtags}
```

**Instagram (caption):**
```
{Title line}
📅 {date}
⏰ {time}
📍 {venue, city}
{Free/cost emoji} {cost}

{1–2 sentences of description}

Link in bio for full details.
.
.
{10–15 hashtags}
```

**Facebook:**
```
{Emoji} {Title}

📅 {date}
⏰ {time}
📍 {full address}
{cost}

{2–3 sentence description}

{link}
{1–2 hashtags}
```

---

### 6. Weekly Roundup (email + social)

**Subject line formulas:**
- `5 Free Things To Do This Weekend in {City}`
- `This Weekend in NoVa: {Event1}, {Event2}, and More`
- `Free Pokémon Events + Weekend Fun in Northern Virginia`

**Body structure:**
```
[Intro: 1–2 sentences, date range, number of events]

[Event 1]
{Title} — {Venue, City}
{Date + Time} · {Free/Cost}
{1-line description}
[Details →]

[Repeat for events 2–5]

[Footer: "More events at novakidlife.com/events"]
```

**Generation prompt:**
```python
ROUNDUP_PROMPT = """Write a weekly family events roundup for Northern Virginia.
Select {n} events from the list below that are:
1. Free or low-cost (prioritize free)
2. Age-appropriate for children under 12
3. Geographically spread across NoVa (not all in same city)
4. Happening this weekend ({start_date} – {end_date})

For each event write:
- Title (exact)
- Venue + City
- Date + Time
- Cost (free / $X)
- 1 engaging sentence about what families will experience

Tone: warm, local, concise. No marketing fluff.

Events: {event_list}
"""
```

---

### 7. Pokémon Product Drop Content

**Set release announcement:**
```
🃏 {Set Name} releases {date}

New cards hitting shelves in Northern Virginia:

Target, Walmart, Best Buy: Check store locator
GameStop: Reserve online for in-store pickup
Costco: Booster bundles (check warehouse)
Nerd Rage Gaming (Manassas): LGS allocation
Battlegrounds (Leesburg/Ashburn): Pre-orders available

Full NoVa buyer's guide → novakidlife.com/pokemon/drops/{slug}
```

**LGS event announcement:**
```
⚡ {Event Type} at {Store Name}

📅 {Date}
⏰ {Time}
📍 {Address, City}
Entry: {cost}
Format: {format}
{Prizes or promo details if known}

Register → {registration_url or store website}
```

---

## AI Generation Prompts (for Lambda enrichment)

### Full description from scraped RawEvent
```python
DESCRIPTION_PROMPT = """Write a family-friendly event description for NovaKidLife.

Event: {title}
Type: {event_type}
Venue: {venue_name}
Location: {location_text}
Date: {start_at}
Tags: {tags}
Source content: {raw_description}

Requirements:
- 100–200 words
- Answer-first: what → when → where → who → cost → how to attend
- Warm, helpful, local tone (see brand guidelines)
- Include specific details from source content
- End with source attribution: "Sourced from {source_name}"
- NO marketing fluff, NO exclamation spam
"""
```

### Short description
```python
SHORT_DESC_PROMPT = """Write a short description for this event. Max 120 characters.
Formula: {What} for {who} at {location}. {Free/cost}.
Event: {title} at {venue_name}, {city}. Free: {is_free}. Cost: {cost_description}.
"""
```
