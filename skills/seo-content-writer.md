---
name: seo-content-writer
description: Write and structure long-form content with proper H2/H3 hierarchy, keyword density, answer-first formatting (Quick Answer block in first 200 words), and FAQ sections. Cross-references seo-content-strategy.md for keyword clusters and topic pillars. Activates when drafting or editing any long-form content.
triggers:
  - body copy
  - article
  - blog post
  - content structure
  - long-form
  - roundup
---

# Skill: SEO Content Writer

**Activation:** Apply when drafting or editing any long-form content — blog posts, location guides, seasonal roundups, "Best of" lists.

**Reference file:** `skills/content-structure-templates.md` — templates for event roundups, neighborhood guides, seasonal content, and "Best of" lists.

---

## Core Principle: Answer First

Every piece of long-form content must lead with a **Quick Answer block** in the first 200 words:
- A numbered or bulleted list of top entries with one-line descriptions
- No images, no links, no JavaScript-dependent content in this block
- Clear heading: `## Quick Answer: Top [N] [Category] in Northern Virginia`
- Purpose: AI systems (Perplexity, ChatGPT, Google AI Overviews) extract this block directly — it's the GEO citation target

---

## H2/H3 Hierarchy Rules

- **H2** = each major section or each item in a list (Google and LLMs use H2s as entity anchors)
- **H3** = sub-items, sub-categories, or FAQ questions within an H2 section
- **Never skip levels** — no H4 without an H3 above it
- **FAQ section** = H2 for the section heading, H3 for each question
- Cross-reference `seo-technical.md` section 3 for per-page-type heading hierarchy

---

## Keyword Integration

Follow the clusters and placement rules in `seo-content-strategy.md`:
- Primary keyword in first 100 words (naturally, not forced)
- Secondary keywords in H2s and body copy
- Geographic modifiers on every page — city names, county names, "Northern Virginia", "NoVa"
- Neighborhood landmarks as entity signals (Reston Town Center, One Loudoun, Tysons Corner, etc.)

---

## Keyword Density

- Primary keyword: 3–5 occurrences per 1,000 words (do not count in headings)
- Never repeat the same phrase more than twice in a paragraph
- Read the paragraph aloud — if it sounds unnatural, remove the extra keyword

---

## FAQ Section — Required on All Long-Form Content

- Minimum 4 questions, maximum 8
- Phrase as conversational parent queries: "What are the best free things to do with kids in Fairfax this weekend?"
- Answers: 40–50 words each — concise enough to be read aloud by voice assistants
- These double as FAQPage JSON-LD schema (cross-reference `seo-schema.md` section 1)
- They are also GEO boosts — AI systems extract FAQ pairs directly from structured content

---

## Verifiable Statistics Over Vague Claims

- Use: "NovaKidLife tracks 200+ family events monthly across 5 Northern Virginia counties"
- Avoid: "We cover hundreds of events"
- Use: "59+ scrape sources" not "many sources"
- Add citations to authoritative external sources (Fairfax County Parks, VisitLoudoun, local news)
- LLMs cite sources that cite other trusted sources — external links to .gov and established local media carry weight

---

## Content Freshness Signals

- Add "Last Updated: [Month Year] — based on events tracked [date range]" to evergreen content
- This is a GEO signal — LLMs deprioritize stale content
- Update seasonal content at the same URL each year (do NOT create new URLs per year)

---

## Internal Linking Rules (from seo-content-strategy.md)

- Every blog post links to at least 3 event pages in the same city/category
- Every blog post links to the events listing (`/events`) or a filtered view
- Every blog post links to 1–2 related blog posts
- Schema: Article minimum; + FAQPage if FAQs; + ItemList if list post

---

## Length Targets

| Content type | Target length |
|-------------|---------------|
| Pillar / location guide | 1,500–3,000 words |
| Supporting post / roundup | 800–1,200 words |
| Event roundup (weekly) | 600–900 words |
| Seasonal guide | 1,200–2,000 words |

---

## Quality Checklist Before Publishing

- [ ] Quick Answer block in first 200 words
- [ ] Primary keyword in first 100 words
- [ ] H2 for each major section, H3 for sub-items
- [ ] FAQ section with 4–8 parent-voice questions
- [ ] "Last Updated" date visible on page
- [ ] 3–5 internal links to event pages
- [ ] 2–3 external links to authoritative sources
- [ ] No vague claims — specific stats and source attribution
- [ ] Article + FAQPage + ItemList (if list) schema included
