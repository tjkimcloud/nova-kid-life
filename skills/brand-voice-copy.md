---
name: brand-voice-copy
description: Copy rules for NovaKidLife event descriptions, short descriptions, social media captions, error states, and email/newsletter — the crisp answer-first voice used in cards and UI elements (not blog posts).
triggers:
  - event description
  - short description
  - UI copy
  - error state
  - empty state
  - email subject
  - newsletter copy
  - copy rules
  - card copy
---

# Skill: Brand Voice — Event Copy & UI

**Activation:** Apply when writing event descriptions, short descriptions, UI error states, or email copy.

> This is the crisp, answer-first voice for cards and UI. For the warm parent-to-parent blog voice — see `brand-voice-blog.md`.

---

## Event Descriptions (full description — event detail page)

**Order always:** what → when → where → who → cost → how to register

- Present tense, active voice
- No marketing fluff in the first paragraph
- Descriptive details that help parents visualize: "kids can touch real farm animals, ride the hayride, and pick their own pumpkin"
- Specifics over vague claims: "ages 3–8" not "young children"
- Source attribution: "Sourced from Fairfax County Library" at the end

**Format:**
```
[What the event is in one sentence, plain language]
[Date, time — specific and complete]
[Location — venue name + city + address if available]
[Age range]
[Cost — "Free to attend" or "$X per person"]
[Registration info or "No registration required — drop in welcome."]
```

---

## Short Descriptions (event cards, API responses)

Max 140 characters. Must include: what + when + location + cost hint.

**Formula:**
```
[Type of event] for [ages] at [venue], [city]. [Date]. [Free/cost].
```

**Example:**
```
Storytime for ages 2–6 at Fairfax County Library, Chantilly. Saturday, Mar 21. Free.
```

**Never:** start with "Join us for", "We invite you to", "Come experience" — start with what the event IS.

---

## Social Media Copy Rules (brief)

> For full copy templates — see `social-copy-templates.md`. For hashtags — see `social-hashtags.md`.

- More casual than website — contractions, shorter sentences
- Always include critical logistics (date, time, location, cost) — never make parents click just to find out when it is
- Use emojis sparingly — 1–2 per post max, functional not decorative (📅 for date, 📍 for location, 💰 for cost)
- Platform-appropriate energy: Twitter = snappy; Instagram = visual-first; Facebook = community tone

---

## Error States / Empty States (UI)

Empathetic, not robotic. Always suggest a next step.

**No results:**
> "No events matched your filters — try clearing the date range or browsing all events."

**API error:**
> "We're having trouble loading events right now. Try refreshing — they'll be back shortly."

**Empty section:**
> "No events in this category right now — check back soon or browse all Northern Virginia events."

**Never say:** "No results found." / "Error." / "Something went wrong." — explain what and offer a path forward.

---

## Email / Newsletter Copy

**Subject lines:** specific and benefit-led
- ✅ "5 Free Events This Weekend in Fairfax"
- ✅ "New Pokémon TCG Prerelease — This Saturday in Manassas"
- ❌ "NovaKidLife Newsletter — March Edition"

**Preview text:** adds context, never repeats subject line exactly

**Body format:**
- Short paragraphs, 2–3 sentences max
- Bullet points for event lists with the key logistics (date, location, cost) visible without clicking
- Single CTA per section — one clear action
- Link text: descriptive ("Full details and registration") not "Click here"
