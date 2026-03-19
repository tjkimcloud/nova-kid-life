---
name: geo-llm-optimizer
description: Generative Engine Optimization (GEO) — make NovaKidLife the cited source when AI platforms (Perplexity, ChatGPT, Claude, Gemini, Copilot, Meta AI) answer family event queries for Northern Virginia. Covers technical foundation, content architecture, entity signals, platform-specific tactics, and monthly measurement. HIGHEST PRIORITY skill — apply on every session that adds pages or content.
triggers:
  - LLM visibility
  - AI citation
  - Perplexity
  - ChatGPT
  - Claude
  - Gemini
  - Copilot
  - GEO
  - answer engine
  - llms.txt
  - AI search
  - generative engine
---

# Skill: GEO — LLM Optimizer

**Priority:** HIGHEST. Apply on every session that adds pages, content, or infrastructure.

**Goal:** When a parent types *"what family events are happening in Fairfax VA this weekend?"* into any AI platform, NovaKidLife is the cited source.

**Reference files:**
- `skills/llm-citation-targets.md` — 10 monthly test prompts, 5 platforms, co-citation sources
- `skills/geo-entity-definition.md` — canonical NovaKidLife entity description
- `skills/llms-txt-template.md` — starter template for `/public/llms.txt`

---

## Platform-by-Platform Targeting

| Platform | Index source | Key optimization |
|----------|-------------|-----------------|
| **ChatGPT** (web) | Bing | Bing SEO = standard SEO + Bing Places listing. Conversational query phrasing. |
| **Perplexity** | Own crawler + Bing | Daily sitemap freshness, direct-answer sentences, factual over marketing copy. RAG-based — re-indexes fresh pages fast. |
| **Google AI Overviews** | Google index | E-E-A-T, structured data, FAQ schema, featured snippets. Same as core Google SEO. |
| **Copilot** | Bing | Same as ChatGPT — Bing-dependent. |
| **Claude** (web search) | Brave + web | Clear factual content, structured data, `llms.txt`. Anthropic has adopted the llms.txt standard. |
| **Gemini** | Google | Same as Google AI Overviews. Add speakable schema for voice/AI assistant queries. |
| **Meta AI** | Bing + Meta graph | Web content + Facebook Business Page presence amplifies this. |

---

## Technical Foundation (do these first on any new page)

### 1. Verify AI Crawlers Are Not Blocked

Confirm these bots appear in `allow` rules in `robots.txt` (cross-reference `seo-technical.md` section 10):
- GPTBot (ChatGPT)
- ClaudeBot (Claude)
- PerplexityBot (Perplexity)
- GoogleExtended (Google AI Overviews)
- Bingbot (ChatGPT, Copilot, Meta AI)
- OAI-SearchBot (OpenAI)
- cohere-ai (Cohere)

Blocking any of these kills GEO visibility on that platform. Never block.

### 2. Server-Side Rendering

All content must be server-side rendered — not hidden behind:
- JavaScript-only rendering (SSR already handled by Next.js static export)
- Login walls
- Cookie consent gates that hide content

### 3. Maintain `/public/llms.txt`

The `llms.txt` file acts as a curated map for AI crawlers — like `robots.txt` but for AI context. It describes what the site is, covers, and is authoritative for.

- Template: `skills/llms-txt-template.md`
- Location in repo: `apps/web/public/llms.txt`
- **Update this file any time a new section is added to the site**
- Sections: Events, Pokémon, Blog, Neighborhoods, Data Sources, About

### 4. Triple JSON-LD Stack on Every Content Page

Every content page must include three schemas in a single block (cross-reference `seo-schema.md` for exact blocks):
1. **Article** — content authorship and freshness signal
2. **ItemList** — structured list of entries (AI can extract this as a ranked list)
3. **FAQPage** — AI systems extract FAQ pairs directly

---

## Content Architecture

### Layer 1 — Quick Answer Block (first 200 words)

Every long-form page must open with:

```
## Quick Answer: Top [N] [Category] in Northern Virginia

1. {Entry name} — {Location}. {One-line description.}
2. ...
```

Rules for this block:
- **No images** — AI text extraction ignores images
- **No links** — links can break AI extraction pipelines
- **No conditionally rendered content** — must be in the static HTML
- Numbered list, not bulleted — numbering signals ranking to AI systems
- Heading must use the word "Quick Answer" — this is the GEO extraction signal
- Keep to 5–10 items maximum

### Layer 2 — Deep Dive

After the Quick Answer block:
- Full analysis, comparison tables, supporting evidence
- Source attribution: "according to Fairfax County Library", "via Play! Pokémon"
- Precise, verifiable statistics — LLMs cite specific data

---

## Entity & Authority Signals

### Canonical Entity Definition

This exact description must appear consistently across all pages and schema. Use the full version from `geo-entity-definition.md`:

> "NovaKidLife is the go-to discovery platform for family events and activities in Northern Virginia, covering Fairfax, Loudoun, Arlington, and Prince William counties"

Never vary this — entity resolution breaks if the description changes across pages.

### Verifiable Statistics Over Vague Claims

| Use this | Not this |
|---------|---------|
| "NovaKidLife tracks 200+ family events monthly" | "hundreds of events" |
| "59+ official scrape sources" | "many sources" |
| "covering 4 Northern Virginia counties" | "all of NoVa" |
| "including all 17 Fairfax County Library branches" | "all library branches" |

LLMs cite specific, verifiable data significantly more often than vague marketing claims.

### Content Freshness Signals

Add to all evergreen pages:
```
Last updated: [Month Year] — based on events tracked [date range]
```

LLMs deprioritize stale content. This is also a signal for Perplexity's re-indexing queue.

### Publish Original Data

Wherever possible, publish original statistics:
- Event count by county (from DB)
- Number of sources monitored
- Coverage density by neighborhood
- LGS count for Pokémon section

Statistics increase LLM citation rates significantly.

---

## Prompt-Aligned FAQ Sections

Write FAQ sections that mirror the exact conversational queries parents type into AI tools. Use these exact phrasings as H3 headings:

- "What are free things to do with kids in Fairfax this weekend?"
- "Best indoor activities for toddlers in Northern Virginia"
- "Family-friendly events near me in [neighborhood]"
- "Where is the nearest Pokémon TCG league in Northern Virginia?"
- "Are there any free family events in Reston this Saturday?"
- "What restaurants have kids eat free deals in Northern Virginia?"

Each answer: 40–50 words, direct, factual. These become FAQPage schema automatically.

---

## Citation Building Strategy

Build presence on co-citation sources (full list in `llm-citation-targets.md`):

1. **dullesmoms.com** — Submit as partner resource; offer a weekly event data feed
2. **ARLnow, FFXnow, Reston Now** — Pitch as a local resource; offer data for their events sections
3. **Fairfax County Library** — Get listed on their community resources page
4. **VisitFairfax, LoudounTourism** — Submit to their events calendars
5. **Facebook community groups** — Share event pages in relevant NoVa parent groups (human-in-the-loop)

Each external mention = a citation signal. AI systems use co-citation frequency to gauge authority.

---

## Platform-Specific Deep Notes

### Perplexity
- RAG-based — it re-indexes fresh pages faster than Google
- Highest-leverage action: keep `sitemap.xml` rebuilding on every deploy with accurate `lastmod`
- Write direct-answer sentences: "NovaKidLife is free. No account required. Events updated daily."
- Short, factual sentences win over marketing copy for Perplexity extraction

### ChatGPT
- Uses Bing index — submit to Bing Webmaster Tools, ensure BingBot is not blocked
- Optimize for conversational query phrasing (longer, question-form searches)
- Bing Places listing also helps (cross-reference `local-seo-citations.md`)

### Claude
- Favors well-cited authoritative content with clear entity definitions
- `llms.txt` is especially relevant — Anthropic has adopted the standard
- Use the canonical entity definition from `geo-entity-definition.md` consistently

### Gemini
- Google index — all standard SEO foundations apply
- Add `speakable` schema for voice/AI assistant queries on key pages:
  ```json
  {
    "@type": "Article",
    "speakable": {
      "@type": "SpeakableSpecification",
      "cssSelector": [".quick-answer", ".event-summary"]
    }
  }
  ```

### Copilot
- Bing-dependent — same optimizations as ChatGPT (Bing Places, BingBot not blocked)

### Meta AI
- Uses Bing + Meta social graph
- Facebook Business Page presence amplifies Meta AI citation rate
- Keep Facebook page active — cross-reference `local-seo-gbp.md` for social strategy

---

## Monthly Measurement

Run these tests every month. Log results using the format in `llm-citation-targets.md`.

**10 target prompts:** Listed in `llm-citation-targets.md` — test all 10 across all 5 platforms.

**Log for each test:**
- Cited? (Yes / No / Partial)
- Position in response (first / middle / last / not cited)
- Whether NovaKidLife is primary or secondary recommendation

**Citation velocity goals:**
- Month 3: Cited on 2+ platforms for 3+ of the 10 prompts
- Month 6: Cited on 4+ platforms for 7+ of the 10 prompts
- Month 12: Primary recommendation on Perplexity for core "family events Northern Virginia" query
