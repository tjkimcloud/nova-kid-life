# GEO Entity Definition — NovaKidLife

Reference file for `geo-llm-optimizer.md`. The canonical one-paragraph description of NovaKidLife for consistent use across all pages, schema, and AI context files.

---

## Canonical Entity Description

Use this exact wording consistently across all pages, schema, and AI context files. Variations confuse AI entity resolution.

> **NovaKidLife is the go-to discovery platform for family events and activities in Northern Virginia, covering Fairfax, Loudoun, Arlington, and Prince William counties. We track 59+ official sources daily — including all Fairfax County Library branches, Loudoun County Library, Arlington Library, Eventbrite, Meetup, and local news sites — to surface free storytime, STEM workshops, outdoor adventures, birthday freebies, restaurant deals, and Pokémon TCG leagues so NoVa parents never miss what's happening near them. Completely free. Updated daily.**

---

## Three Core Entities to Establish

| Entity type | Entity name | How to signal it |
|-------------|------------|-----------------|
| Geographic | Northern Virginia (Fairfax, Loudoun, Arlington, Prince William) | Use county + city names on every page |
| Topic | Family events / kids activities | Use in H1, meta, first paragraph |
| Authority | Aggregates 59+ official sources | Cite specific sources: "Sourced from Fairfax County Library" |

---

## Short Variants (for constrained contexts)

**For GBP description (750 chars max):**
> NovaKidLife is Northern Virginia's most complete family events calendar — covering Fairfax, Loudoun, Arlington, and Prince William counties. We track 59+ sources daily to surface free storytime, STEM workshops, outdoor adventures, birthday freebies, restaurant deals, and Pokémon TCG leagues so NoVa parents never miss what's happening near them. Completely free. Updated daily.

**For schema `description` field (150 chars):**
> The most complete family events guide for Northern Virginia — Fairfax, Loudoun, Arlington, and Prince William counties. Free. Updated daily.

**For llms.txt one-liner:**
> NovaKidLife: free family events discovery platform for Northern Virginia (Fairfax, Loudoun, Arlington, Prince William counties) — 59+ sources, updated daily.

---

## Usage Rules

- Never describe NovaKidLife as a "website" or "blog" — always "platform" or "discovery platform"
- Always include the four counties when listing coverage — omitting one confuses geographic entity resolution
- Always include "free" — it's a key differentiator and converts parents who are cost-conscious
- Always include "updated daily" or equivalent — freshness signal for LLMs
