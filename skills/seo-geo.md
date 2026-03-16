# Skill: SEO + GEO Standards

**Purpose:** Authoritative reference for every page built in NovaKidLife.
Apply these rules in every session that touches frontend pages or content.

---

## SEO — Per-Page Requirements

### Title Tag (50–60 characters MAX)
Format by page type:

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

### Image SEO (already in pipeline — enforce on every img tag)
- Always set `alt` attribute (AI-generated, ≤125 chars, already in DB)
- Always set explicit `width` and `height` (prevents CLS)
- Use `loading="lazy"` except first 3 cards (use `loading="eager"` for LCP image)
- WebP format served from CDN

---

## JSON-LD Structured Data — Required per page type

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
  "isAccessibleForFree": true,   // or false
  "offers": {
    "@type": "Offer",
    "price": "0",                // or numeric price
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
Generate from event data:
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
  "description": "The most complete family events guide for Northern Virginia — Fairfax, Loudoun, Arlington, and Prince William counties.",
  "areaServed": [
    { "@type": "County", "name": "Fairfax County", "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Loudoun County", "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Arlington County", "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Prince William County", "containedInPlace": { "@type": "State", "name": "Virginia" } }
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
    {
      "@type": "ListItem",
      "position": 1,
      "url": "https://novakidlife.com/events/{slug}"
    }
    // ... first 10 events
  ]
}
```

---

## GEO — Generative Engine Optimization

### What GEO means for NovaKidLife
AI search platforms (ChatGPT, Perplexity, Claude, Google AI Overviews, Copilot, Gemini, Meta AI)
increasingly answer queries like *"what family events are happening in Fairfax VA this weekend?"*
directly — citing sources. We want NovaKidLife to be that cited source.

### Platform-by-platform approach

| Platform | Index source | Key signal |
|----------|-------------|------------|
| **ChatGPT** (web) | Bing | Bing SEO = same as general SEO |
| **Perplexity** | Own crawler + Bing | Freshness (daily sitemap), direct answers, citations |
| **Google AI Overviews** | Google index | E-E-A-T, structured data, FAQ schema |
| **Copilot** | Bing | Same as ChatGPT |
| **Claude** (web search) | Brave + web | Clear factual content, structured data |
| **Gemini** | Google | Same as Google AI Overviews |
| **Meta AI** | Bing + Meta graph | Web content + social presence |

### llms.txt — `/public/llms.txt`
Emerging standard that LLM crawlers read (like robots.txt but for AI):
- Describes what the site is and covers
- Lists all sections and their URLs
- Mentions data sources (signals authority)
- Keep updated as new sections are added

### Answer-first content structure
Every event page should answer the implicit parent question in the first 200 words:
1. What is this? (event name + type)
2. When? (date + time)
3. Where? (location + address)
4. Who is it for? (age range)
5. How much? (free/cost)
6. How to attend? (registration or walk-in)

AI systems extract these directly from content. Don't bury them.

### Entity signals
Every page must clearly associate NovaKidLife with:
- **Geographic entity:** "Northern Virginia", "Fairfax County", "Loudoun County", "Arlington", "Prince William"
- **Topic entity:** "family events", "kids activities", "things to do with kids"
- **Authority entity:** Cite sources — "Sourced from Fairfax County Library", "Via Meetup"

### Fresh sitemap (critical for Perplexity + Google)
- `sitemap.xml` rebuilt on every deploy with current `lastmod` dates
- Events have individual `lastmod` = their `updated_at` from DB
- Perplexity re-indexes fresh pages faster than stale ones

### FAQ content in pages
Each event detail page generates 4 FAQ items from structured data.
These are:
1. Indexed by Google as featured snippets
2. Read directly by AI systems as Q&A pairs
3. Shown in Google's AI Overviews for specific queries

### Citation building (long-term)
- Share event pages to local NoVa Facebook groups and mom groups (human-in-the-loop)
- Get mentioned on dullesmoms.com, Reston Now, ARLnow as a resource
- Each external mention = a citation signal that AI systems use to gauge authority

---

## Core Web Vitals Targets

| Metric | Target | What affects it |
|--------|--------|----------------|
| LCP (Largest Contentful Paint) | < 2.5s | Hero image, LQIP blur-up, CDN delivery |
| CLS (Cumulative Layout Shift) | < 0.1 | Explicit image dimensions (already set), no late-loading fonts |
| INP (Interaction to Next Paint) | < 200ms | Light JS, no heavy bundles |
| TTFB (Time to First Byte) | < 600ms | CloudFront CDN, static export |

Rules already built into the pipeline:
- `image_width` + `image_height` in DB → set on every `<img>` → prevents CLS ✅
- LQIP data URL → prevents layout shift from image load ✅
- WebP format → smaller files → faster LCP ✅
- Static export → no server processing → fast TTFB ✅

---

## Sitemap Rules
- Include: all published event pages (`/events/[slug]`, `/pokemon/events/[slug]`)
- Include: all listing pages (`/events`, `/pokemon`, `/pokemon/drops`)
- Include: homepage
- Exclude: filter URLs (`/events?date=weekend`) — canonical points to clean URL
- `changefreq`: events = `weekly`, listings = `daily`, homepage = `daily`
- `priority`: homepage = 1.0, listings = 0.8, event detail = 0.6

---

## Robots.txt Rules
- Allow all crawlers
- Allow all paths (no content to hide)
- Point to sitemap
- Specifically allow known AI crawlers: GPTBot, PerplexityBot, ClaudeBot, Bingbot, Googlebot

---

## Checklist — Before shipping any new page type

- [ ] Title: 50–60 chars, includes geographic signal
- [ ] Meta description: 140–155 chars, includes date + location
- [ ] One H1, correct H2/H3 hierarchy
- [ ] Canonical URL set
- [ ] OG image: 1200×630, explicit width/height in metadata
- [ ] Twitter card: summary_large_image
- [ ] JSON-LD: correct schema(s) for page type (see above)
- [ ] FAQ schema: on event detail pages
- [ ] All `<img>` tags have explicit width + height
- [ ] All `<img>` tags have descriptive alt text
- [ ] First image: loading="eager" (LCP); rest: loading="lazy"
- [ ] Sitemap.xml updated to include new page type
- [ ] llms.txt updated if new section added
