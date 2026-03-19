# Skill: SEO + GEO — Complete Standards

**Purpose:** Authoritative SEO + GEO reference for NovaKidLife. Covers technical SEO,
on-page strategy, local SEO, E-E-A-T, content architecture, GEO, analytics, and competitive
positioning. Apply every session that touches frontend pages, content, or infrastructure.

---

## 1. Technical SEO — Per-Page Requirements

### Title Tag (50–60 characters MAX)

| Page | Format | Example |
|------|--------|---------|
| Event detail | `{Event Title} — {City}, VA \| NovaKidLife` | `Storytime at Fairfax Library — Fairfax, VA \| NovaKidLife` |
| Events listing | `Family Events in Northern Virginia \| NovaKidLife` | — |
| Pokémon hub | `Pokémon TCG Events in Northern Virginia \| NovaKidLife` | — |
| Pokémon event | `{Event} — {City}, VA Pokémon TCG \| NovaKidLife` | — |
| Product drop | `{Set Name} Pokémon TCG — Where to Buy in NoVa \| NovaKidLife` | — |
| Homepage | `NovaKidLife — Family Events in Northern Virginia` | — |

Rules:
- Always include a Virginia/NoVa geographic signal — local SEO ranking factor
- Never truncate mid-word — use `…` if needed
- Count pipes `|` and dashes as characters

### Meta Description (140–155 characters MAX)
Format for event pages:
```
{Day}, {Month} {Date} · {Time} at {Location}. {Description snippet, ~60 chars}. {Free/Cost}.
```
Example (152 chars):
```
Sat, Mar 21 · 10:00 AM at Fairfax County Library. Free storytime for kids ages 2–6 in Fairfax, VA. Register now — spots fill quickly.
```

Rules:
- Include the date — parents search "events this Saturday"
- Include the location — local SEO signal
- Include free/cost — high-intent filter for parents
- End with mild CTA or key benefit
- No keyword stuffing — write for the parent, not the algorithm

### Heading Hierarchy — ONE H1 per page, strictly

**Event detail page:**
```
<h1> {Event Title}                    ← unique, matches title tag
<h2> About This Event                 ← description section
<h2> Event Details                    ← date/time/location/cost
<h2> How to Register                  ← only if registration_url exists
<h2> Frequently Asked Questions       ← FAQ section (GEO boost)
<h2> Similar Events Near You          ← related events section
  <h3> {Related Event Title 1}
  <h3> {Related Event Title 2}
  <h3> {Related Event Title 3}
```

**Events listing page:**
```
<h1> Family Events in Northern Virginia
<h2> [filter/section labels if used]
<h3> {Each event card title}          ← EventCard uses <h3> inside grid
```

**Pokémon hub:**
```
<h1> Pokémon TCG Events in Northern Virginia
<h2> Upcoming Leagues & Tournaments
  <h3> {Each event title}
<h2> New Set Releases
  <h3> {Each set name}
<h2> Where to Buy in Northern Virginia
  <h3> Local Game Stores
  <h3> Big Box Retailers
```

### Canonical URLs
Every page must have a canonical tag pointing to the clean URL (no query params):
```tsx
alternates: { canonical: 'https://novakidlife.com/events/slug' }
```

### Open Graph (every page)
```tsx
openGraph: {
  title:       '{optimized title}',
  description: '{optimized description}',
  type:        'article',   // event detail pages
  images: [{
    url:    event.og_image_url,   // 1200×630 WebP from S3
    width:  1200,
    height: 630,
    alt:    event.image_alt,
  }],
}
```

### Twitter Card
```tsx
twitter: {
  card:        'summary_large_image',
  title:       '{title}',
  description: '{description}',
  images:      [event.og_image_url],
}
```

### Image SEO (enforce on every img tag)
- Always set `alt` attribute (AI-generated, ≤125 chars, already in DB)
- Always set explicit `width` and `height` (prevents CLS)
- Use `loading="lazy"` except first 3 cards (use `loading="eager"` for LCP image)
- WebP format served from CDN with 1-year cache headers
- Serve responsive images via `srcset`: hero-sm (400px), hero-md (800px), hero (1200px)

---

## 2. JSON-LD Structured Data — Required per page type

### Event detail page — 3 schemas

**1. Event schema (rich results in Google)**
```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "{title}",
  "description": "{description, first 500 chars}",
  "startDate": "{ISO 8601 with timezone, e.g. 2026-03-21T10:00:00-04:00}",
  "endDate": "{ISO 8601 or omit if null}",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "{location_name}",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "{location_address}",
      "addressLocality": "{city}",
      "addressRegion": "VA",
      "addressCountry": "US"
    }
  },
  "image": ["{og_image_url}", "{image_url}"],
  "organizer": {
    "@type": "Organization",
    "name": "NovaKidLife",
    "url": "https://novakidlife.com"
  },
  "isAccessibleForFree": true,
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "{registration_url or event page url}"
  },
  "url": "https://novakidlife.com/events/{slug}"
}
```

**2. BreadcrumbList schema**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home",   "item": "https://novakidlife.com" },
    { "@type": "ListItem", "position": 2, "name": "Events", "item": "https://novakidlife.com/events" },
    { "@type": "ListItem", "position": 3, "name": "{event title}" }
  ]
}
```

**3. FAQPage schema (GEO boost — AI systems pull these directly)**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is {title} free?",
      "acceptedAnswer": { "@type": "Answer", "text": "Yes, {title} is free to attend." }
    },
    {
      "@type": "Question",
      "name": "Where is {title} held?",
      "acceptedAnswer": { "@type": "Answer", "text": "{title} is held at {location_name} in {city}, Virginia." }
    },
    {
      "@type": "Question",
      "name": "What age is {title} for?",
      "acceptedAnswer": { "@type": "Answer", "text": "{Age range or 'All ages welcome'}" }
    },
    {
      "@type": "Question",
      "name": "How do I register for {title}?",
      "acceptedAnswer": { "@type": "Answer", "text": "{Registration info or 'No registration required.'}" }
    }
  ]
}
```

### Homepage — 2 schemas

**WebSite schema (enables Google sitelinks searchbox)**
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "NovaKidLife",
  "url": "https://novakidlife.com",
  "description": "Family events discovery platform for Northern Virginia",
  "potentialAction": {
    "@type": "SearchAction",
    "target": { "@type": "EntryPoint", "urlTemplate": "https://novakidlife.com/events?q={search_term_string}" },
    "query-input": "required name=search_term_string"
  }
}
```

**LocalBusiness schema**
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "NovaKidLife",
  "url": "https://novakidlife.com",
  "description": "The most complete family events guide for Northern Virginia.",
  "areaServed": [
    { "@type": "County", "name": "Fairfax County",       "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Loudoun County",       "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Arlington County",     "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Prince William County","containedInPlace": { "@type": "State", "name": "Virginia" } }
  ],
  "knowsAbout": ["Family Events", "Kids Activities", "Northern Virginia", "Pokémon TCG Events"]
}
```

### Events listing page — ItemList schema
```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Family Events in Northern Virginia",
  "description": "Upcoming family events and kids activities in Northern Virginia",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "url": "https://novakidlife.com/events/{slug}" }
  ]
}
```

---

## 3. Keyword Strategy

### Search Intent Classification
Every page must be mapped to one primary intent:

| Intent | Description | NovaKidLife pages |
|--------|-------------|-------------------|
| **Navigational** | User knows the brand | Homepage |
| **Informational** | "What events are near me?" | Listing pages, category pages |
| **Transactional** | "Register for storytime" | Event detail pages |
| **Local** | "Free kids events Fairfax VA this weekend" | All pages — primary intent |

### Primary Keyword Clusters

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

### Keyword Placement Rules
- Primary keyword in: H1, first 100 words, title tag, meta description, image alt, URL slug
- Secondary keywords in: H2s, body copy (naturally), image file names (already slugified)
- Never force keywords — if it reads awkwardly, remove it
- Geographic modifiers on every page (VA, Virginia, Northern Virginia, NoVa, county names)

### URL Structure
```
/events/[event-slug]              ← event title + location + date in slug
/events?category=storytime        ← filterable listing (canonical = /events)
/pokemon/events/[slug]            ← pokemon section
```
Slug format: `{event-type}-{location}-{month}-{day}` e.g. `storytime-fairfax-library-march-21`

---

## 4. Local SEO

> **Full local SEO reference is in `skills/local-seo.md`** — covers GBP setup, citation tiers,
> hyperlocal content, blog strategy, neighborhood targeting, local link building, schema for
> local, Pokémon TCG local SEO, and a complete launch timeline. That file is the authoritative
> source. The summary below is a quick reference only.

### Google Business Profile (GBP) — Set up at launch
- Business name: `NovaKidLife`
- Category: `Event planning service` + `Children's party service`
- Service area: Fairfax County, Loudoun County, Arlington County, Prince William County
- Description: Include "family events", "Northern Virginia", "kids activities"
- Posts: Add new events as GBP posts weekly (links back to site)
- Q&A: Seed 5 common questions + answers

### NAP Consistency (Name, Address, Phone)
For a web-only business:
- Use consistent name `NovaKidLife` everywhere (no variations)
- List city as `Northern Virginia, VA` or `Fairfax, VA` consistently
- No phone required — use contact form/email

### Local Citations — Build in order of priority
1. **Google Business Profile** (most important)
2. **Bing Places** (ChatGPT + Copilot use Bing)
3. **Apple Maps** (iOS users)
4. **Yelp** (service business listing)
5. **Facebook Business Page** (already have)
6. **Nextdoor** (neighborhood-level visibility — high NoVa parent usage)
7. **Patch.com** (local news, already scraped as source — become a source too)
8. **dullesmoms.com** (submit as a resource)
9. **ARLnow, FFXnow, Reston Now** (pitch as a local resource)

### Local Link Building
- Partner with Fairfax County Library system — request a link from their community resources page
- Get listed on `visitfairfax.org` and `loudountourism.org` events calendars
- Submit to `washington.org/events` (DC tourism board covers NoVa)
- Connect with NoVa mom bloggers / parenting influencers — offer to feature their event picks

---

## 5. E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness)

Google's quality rater framework. Critical for local/family content.

### Experience
- Add "About NovaKidLife" page: real person behind the site, why they built it, personal connection to NoVa families
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

## 6. Content Architecture

### Topic Cluster Model
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

### Internal Linking Strategy
- Every event detail page → links to 3 related events (already built: RelatedEvents component)
- Every event detail page → links back to `/events` listing (already built: Breadcrumbs)
- Events listing page → links to featured/upcoming events (above the fold)
- Homepage → links to `/events`, `/pokemon`, featured events
- **Rule:** No page should be more than 2 clicks from the homepage
- **Rule:** Every new event page gets at least 1 inbound internal link automatically (via RelatedEvents)

### Content Freshness
- Events expire naturally — keep sitemap `lastmod` accurate
- Add a `lastmod` = `updated_at` column to sitemap entries (already done)
- Consider a "This Week's Events" or "Weekend Picks" editorial section at launch (human-curated, high E-E-A-T)
- Stale events (past `end_at`) should return 410 Gone or redirect to `/events` — do NOT leave up dead pages

---

## 7. GEO — Generative Engine Optimization

### What GEO means for NovaKidLife
AI search platforms (ChatGPT, Perplexity, Claude, Google AI Overviews, Copilot, Gemini, Meta AI)
increasingly answer queries like *"what family events are happening in Fairfax VA this weekend?"*
directly — citing sources. We want NovaKidLife to be that cited source.

### Platform-by-platform targeting

| Platform | Index source | Key optimization |
|----------|-------------|-----------------|
| **ChatGPT** (web) | Bing | Bing SEO = standard SEO + Bing Places listing |
| **Perplexity** | Own crawler + Bing | Daily sitemap freshness, direct answers, citations |
| **Google AI Overviews** | Google index | E-E-A-T, structured data, FAQ schema, featured snippets |
| **Copilot** | Bing | Same as ChatGPT |
| **Claude** (web search) | Brave + web | Clear factual content, structured data, `llms.txt` |
| **Gemini** | Google | Same as Google AI Overviews |
| **Meta AI** | Bing + Meta graph | Web content + Facebook page presence |

### llms.txt — `/public/llms.txt`
Emerging standard that LLM crawlers read (like `robots.txt` but for AI):
- Describes what the site is, covers, and is authoritative for
- Lists all sections and their URLs
- Mentions data sources (signals to AI: "this site aggregates from 59 official sources")
- Keep updated as new sections are added

### Answer-first content structure
Every event page answers the implicit parent question in the first 200 words:
1. **What is this?** (event name + type)
2. **When?** (date + time)
3. **Where?** (location + address)
4. **Who is it for?** (age range)
5. **How much?** (free/cost)
6. **How to attend?** (registration or walk-in)

AI systems extract these directly from content. Never bury the key facts.

### Entity signals
Every page must clearly associate NovaKidLife with:
- **Geographic entity:** "Northern Virginia", "Fairfax County", "Loudoun County", "Arlington", "Prince William"
- **Topic entity:** "family events", "kids activities", "things to do with kids"
- **Authority entity:** Cite sources — "Sourced from Fairfax County Library", "Via Meetup"

### Perplexity-specific optimization
Perplexity cites sources heavily and re-indexes fresh pages fast:
- Keep `sitemap.xml` rebuilding on every deploy with accurate `lastmod`
- Write event descriptions that directly answer questions ("Is storytime free at Fairfax Library? Yes — free drop-in, no registration required.")
- Short, factual sentences win over marketing copy for AI extraction

### Citation building (compounding authority)
- Share event pages to local NoVa Facebook groups and mom groups (human-in-the-loop)
- Get mentioned on dullesmoms.com, Reston Now, ARLnow as a resource
- Each external mention = a citation signal that AI systems use to gauge authority
- NovaKidLife appearing in local news = AI systems treat it as authoritative local source

---

## 8. Core Web Vitals

| Metric | Target | What affects it |
|--------|--------|----------------|
| LCP (Largest Contentful Paint) | < 2.5s | Hero image, LQIP blur-up, CDN delivery |
| CLS (Cumulative Layout Shift) | < 0.1 | Explicit image dimensions (already set), no late fonts |
| INP (Interaction to Next Paint) | < 200ms | Light JS, no heavy bundles |
| TTFB (Time to First Byte) | < 600ms | CloudFront CDN, static export |

Rules already built into the pipeline:
- `image_width` + `image_height` in DB → set on every `<img>` → prevents CLS ✅
- LQIP data URL → prevents layout shift from image load ✅
- WebP format → smaller files → faster LCP ✅
- Static export → no server processing → fast TTFB ✅
- Self-hosted fonts with `font-display: swap` → no FOIT ✅

Additional checks for Session 11:
- Verify no render-blocking scripts in `<head>`
- Verify `next/font` preloads are in place
- Verify CloudFront compression (gzip/br) is enabled
- Check JS bundle size with `npm run build` output

---

## 9. Sitemap Rules
- Include: all published event pages (`/events/[slug]`, `/pokemon/events/[slug]`)
- Include: all listing pages (`/events`, `/pokemon`, `/pokemon/drops`)
- Include: homepage
- Exclude: filter URLs (`/events?date=weekend`) — canonical points to clean URL
- `changefreq`: events = `weekly`, listings = `daily`, homepage = `daily`
- `priority`: homepage = 1.0, listings = 0.8, event detail = 0.6
- Submit to Google Search Console and Bing Webmaster Tools at launch

---

## 10. Robots.txt Rules
- Allow all crawlers
- Allow all paths
- Point to sitemap
- Explicitly allow known AI crawlers: GPTBot, PerplexityBot, ClaudeBot, Bingbot, Googlebot, OAI-SearchBot, cohere-ai

---

## 11. Analytics & Measurement

### What to track from day 1
**Google Search Console (free, essential)**
- Index coverage — are event pages being indexed?
- Search queries — what are people actually searching to find us?
- Click-through rates by page — which titles/descriptions underperform?
- Core Web Vitals report — field data from real users
- Rich results — are Event schema rich results appearing?

**Google Analytics 4 (or Plausible for privacy-first)**
Key events to track:
- `event_page_view` — with event slug, section, event_type
- `filter_applied` — which filters parents use most
- `search_performed` — semantic search queries
- `register_click` — clicks on registration links (revenue signal)
- `share_click` — social sharing (virality signal)
- `newsletter_subscribe` — email list growth

**Key KPIs at launch**
| KPI | Target (month 3) | Target (month 6) |
|-----|-----------------|-----------------|
| Organic sessions/month | 500 | 5,000 |
| Indexed pages | 100+ | 500+ |
| GBP impressions/month | 200 | 1,000 |
| Email subscribers | 50 | 500 |
| Event detail avg. time on page | > 45s | > 60s |
| Lighthouse score (all pages) | 90+ | 95+ |

### SEO health monitoring (add to Session 12 CloudWatch)
- Broken link checker (weekly crawl)
- Sitemap submission freshness
- 404 rate spike alert
- Search Console coverage errors

---

## 12. Competitive Positioning

### Direct competitors in NoVa family events space
- **Eventbrite** — massive but unfocused, no local curation
- **Meetup** — adult-skewing, poor family UX
- **dullesmoms.com** — human-curated blog, no structured data, no search
- **Patch.com** — local news, events section is thin
- **NoVa Parks website** — official but poor UX, no aggregation

### NovaKidLife advantages to amplify in content
1. **Aggregation breadth** — 59 sources vs. anyone else's 1–2
2. **Pokémon TCG niche** — zero competition for NoVa TCG content
3. **Free events focus** — explicit free filter, #FreeKidsEvents positioning
4. **AI-powered search** — semantic search ("outdoor activities for toddlers") vs. keyword search
5. **Mobile-first UX** — parents search on phones at the last minute

### Content differentiation
- Write as if you're a NoVa parent, not a tourism board
- Use neighborhood names (Reston Town Center, Mosaic District, One Loudoun) not just county names
- Acknowledge the "busy parent" reality in copy — "no registration required", "drop-in welcome"

---

## 13. Pre-Ship Checklist — Every new page type

- [ ] Title: 50–60 chars, includes geographic signal
- [ ] Meta description: 140–155 chars, includes date + location
- [ ] One H1, correct H2/H3 hierarchy
- [ ] Canonical URL set
- [ ] OG image: 1200×630, explicit width/height in metadata
- [ ] Twitter card: `summary_large_image`
- [ ] JSON-LD: correct schema(s) for page type (see section 2)
- [ ] FAQ schema on event detail pages
- [ ] All `<img>` tags have explicit width + height
- [ ] All `<img>` tags have descriptive alt text (≤125 chars)
- [ ] First image: `loading="eager"` (LCP); rest: `loading="lazy"`
- [ ] Sitemap.xml includes new page type
- [ ] llms.txt updated if new section added
- [ ] Internal links: page is reachable within 2 clicks from homepage
- [ ] Related content links present (RelatedEvents component)
- [ ] Lighthouse score ≥ 90 (Performance, Accessibility, Best Practices, SEO)
- [ ] No broken links
- [ ] Google Search Console: submit URL for indexing after deploy
