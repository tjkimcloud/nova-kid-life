---
name: seo-content-strategy
description: Content strategy, keyword clusters, search intent, URL structure, E-E-A-T, topic cluster pillars, internal linking architecture, content freshness rules, and competitive positioning for NovaKidLife. Activates when planning content, writing copy, or designing new page types.
triggers:
  - keyword
  - content plan
  - topic cluster
  - internal linking
  - E-E-A-T
  - pillar page
  - URL structure
  - competitive
  - search intent
---

# Skill: SEO Content Strategy

**Activation:** Apply when planning content, writing copy, or designing new page types.

---

## 1. Search Intent Classification

Every page must be mapped to one primary intent:

| Intent | Description | NovaKidLife pages |
|--------|-------------|-------------------|
| **Navigational** | User knows the brand | Homepage |
| **Informational** | "What events are near me?" | Listing pages, category pages |
| **Transactional** | "Register for storytime" | Event detail pages |
| **Local** | "Free kids events Fairfax VA this weekend" | All pages — primary intent |

---

## 2. Primary Keyword Clusters

**Cluster 1 — General family events (highest volume)**
- `family events northern virginia`
- `kids activities northern virginia this weekend`
- `things to do with kids in fairfax va`
- `free kids events nova`
- `family friendly events dc suburbs`

**Cluster 2 — City-specific (high local intent)**
- `things to do with kids in [city]` (Fairfax, Reston, Chantilly, Herndon, McLean, Leesburg, Manassas, Sterling, Alexandria, Woodbridge)
- `free kids events [city] this weekend`
- `family events [city] VA`

**Cluster 3 — Event type (medium volume, high conversion)**
- `storytime fairfax county library`
- `kids cooking classes northern virginia`
- `stem activities kids nova`
- `outdoor family activities nova`
- `birthday freebies northern virginia`

**Cluster 4 — Pokémon TCG (niche, zero competition)**
- `pokemon tcg league northern virginia`
- `pokemon prerelease nova`
- `where to buy pokemon cards northern virginia`
- `nerd rage gaming pokemon`
- `pokemon tournament fairfax va`

**Cluster 5 — Deal/freebie (high parent intent)**
- `kids eat free northern virginia`
- `free family events nova this week`
- `restaurant deals kids nova`

---

## 3. Keyword Placement Rules

- Primary keyword in: H1, first 100 words, title tag, meta description, image alt, URL slug
- Secondary keywords in: H2s, body copy (naturally), image file names (already slugified)
- Never force keywords — if it reads awkwardly, remove it
- Geographic modifiers on every page (VA, Virginia, Northern Virginia, NoVa, county names)

---

## 4. URL Structure

```
/events/[event-slug]              ← event title + location + date in slug
/events?category=storytime        ← filterable listing (canonical = /events)
/pokemon/events/[slug]            ← pokemon section
```

Slug format: `{event-type}-{location}-{month}-{day}` e.g. `storytime-fairfax-library-march-21`

---

## 5. E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)

Google's quality rater framework — critical for local/family content.

### Experience
- "About NovaKidLife" page: real person behind the site, why they built it, personal connection to NoVa families
- Author bylines on any editorial content (blog posts, roundups)
- Include real photos of NoVa locations and events (not just AI-generated)

### Expertise
- Source attribution on every event: "Sourced from Fairfax County Library", "Via Meetup"
- Accurate, up-to-date event details (auto-pulled from official sources)
- Pokémon TCG section shows domain expertise (formats, deck archetypes, tournament structure)

### Authoritativeness
- Get mentioned/cited by local news (ARLnow, FFXnow, Reston Now, InsideNova)
- Be listed in official county resources pages
- Social proof: follower counts, post engagement once accounts grow
- Press mentions page (add at launch)

### Trustworthiness
- HTTPS (CloudFront handles this)
- Clear privacy policy and terms of service pages (add at launch)
- Contact page / email address visible
- No broken links (CI/CD Lighthouse check catches these)
- No misleading event info — verify scraper accuracy before launch

---

## 6. Topic Cluster Model

Structure content around pillar pages with supporting spokes:

**Pillar 1: Family Events in Northern Virginia** (main pillar)
- Hub: `/events` listing page
- Spokes: individual event detail pages, category pages (storytime, STEM, outdoor)
- Internal links: every event links back to `/events` and to related events

**Pillar 2: Free Kids Events NoVa** (high-intent pillar)
- Hub: `/events?free=true` (or a dedicated `/free-events` page — consider adding)
- Spokes: free event detail pages, birthday freebies section
- Content angle: "You shouldn't have to pay to find free events"

**Pillar 3: Pokémon TCG in Northern Virginia** (niche authority pillar)
- Hub: `/pokemon`
- Spokes: league events, prereleases, product drops, retailer matrix
- Internal links: retailer pages link to each other, events link to drops calendar

**Pillar 4: Things to Do in [City]** (local pillar — future)
- Hub: `/locations/fairfax-va`, `/locations/reston-va` etc.
- Spokes: events in that city
- Currently handled by filter URLs — consider dedicated location landing pages

---

## 7. Internal Linking Architecture

- Every event detail page → links to 3 related events (already built: RelatedEvents component)
- Every event detail page → links back to `/events` listing (already built: Breadcrumbs)
- Events listing page → links to featured/upcoming events (above the fold)
- Homepage → links to `/events`, `/pokemon`, featured events
- **Rule:** No page should be more than 2 clicks from the homepage
- **Rule:** Every new event page gets at least 1 inbound internal link automatically (via RelatedEvents)

---

## 8. Content Freshness Rules

- Events expire naturally — keep sitemap `lastmod` accurate
- Add a `lastmod` = `updated_at` column to sitemap entries (already done)
- Consider a "This Week's Events" or "Weekend Picks" editorial section at launch (human-curated, high E-E-A-T)
- Stale events (past `end_at`) should return 410 Gone or redirect to `/events` — do NOT leave up dead pages

---

## 9. Competitive Positioning

### Direct competitors in NoVa family events space
- **Eventbrite** — massive but unfocused, no local curation
- **Meetup** — adult-skewing, poor family UX
- **dullesmoms.com** — human-curated blog, no structured data, no search
- **Patch.com** — local news, events section is thin
- **NoVa Parks website** — official but poor UX, no aggregation

### NovaKidLife advantages to amplify in all content
1. **Aggregation breadth** — 59+ sources vs. anyone else's 1–2
2. **Pokémon TCG niche** — zero competition for NoVa TCG content
3. **Free events focus** — explicit free filter, #FreeKidsEvents positioning
4. **AI-powered search** — semantic search ("outdoor activities for toddlers") vs. keyword search
5. **Mobile-first UX** — parents search on phones at the last minute

### Content differentiation voice
- Write as if you're a NoVa parent, not a tourism board
- Use neighborhood names (Reston Town Center, Mosaic District, One Loudoun) not just county names
- Acknowledge the "busy parent" reality in copy — "no registration required", "drop-in welcome"
