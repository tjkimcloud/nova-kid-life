---
name: seo-technical
description: Technical SEO enforcement for NovaKidLife — title tags, meta descriptions, heading hierarchy, canonical URLs, Open Graph, Twitter cards, image SEO, Core Web Vitals, sitemap rules, robots.txt, and the full pre-ship checklist. Activate any time a frontend page is touched or a new page type is added.
triggers:
  - title tag
  - meta description
  - H1
  - canonical
  - OG image
  - Core Web Vitals
  - Lighthouse
  - pre-ship
  - sitemap
  - robots.txt
---

# Skill: SEO Technical — Enforcement Reference

**Activation:** Apply on every session that touches a frontend page or adds a new page type.

---

## 1. Title Tag (50–60 characters MAX)

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

---

## 2. Meta Description (140–155 characters MAX)

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

---

## 3. Heading Hierarchy — ONE H1 per page, strictly

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

---

## 4. Canonical URLs

Every page must have a canonical tag pointing to the clean URL (no query params):
```tsx
alternates: { canonical: 'https://novakidlife.com/events/slug' }
```

Filter URLs (`/events?date=weekend`) are NOT canonical — canonical always points to clean URL.

---

## 5. Open Graph (every page)

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

---

## 6. Twitter Card (every page)

```tsx
twitter: {
  card:        'summary_large_image',
  title:       '{title}',
  description: '{description}',
  images:      [event.og_image_url],
}
```

---

## 7. Image SEO (enforce on every img tag)

- Always set `alt` attribute (AI-generated, ≤125 chars, already in DB)
- Always set explicit `width` and `height` (prevents CLS)
- Use `loading="lazy"` except first 3 cards (use `loading="eager"` for LCP image)
- WebP format served from CDN with 1-year cache headers
- Serve responsive images via `srcset`: hero-sm (400px), hero-md (800px), hero (1200px)

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

Additional checks before any new deploy:
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
- `lastmod` must equal `updated_at` from the DB for every event page

---

## 10. Robots.txt Rules

- Allow all crawlers
- Allow all paths
- Point to sitemap
- Explicitly allow known AI crawlers: GPTBot, PerplexityBot, ClaudeBot, Bingbot, Googlebot, OAI-SearchBot, cohere-ai
- Never block any of the above — doing so kills GEO visibility (cross-reference `geo-llm-optimizer.md`)

---

## 11. Pre-Ship Checklist — Every new page type

Run through before every `npm run build` and deploy:

- [ ] Title: 50–60 chars, includes geographic signal
- [ ] Meta description: 140–155 chars, includes date + location
- [ ] One H1, correct H2/H3 hierarchy
- [ ] Canonical URL set
- [ ] OG image: 1200×630, explicit width/height in metadata
- [ ] Twitter card: `summary_large_image`
- [ ] JSON-LD: correct schema(s) for page type (cross-reference `seo-schema.md`)
- [ ] FAQ schema on event detail pages
- [ ] All `<img>` tags have explicit width + height
- [ ] All `<img>` tags have descriptive alt text (≤125 chars)
- [ ] First image: `loading="eager"` (LCP); rest: `loading="lazy"`
- [ ] Sitemap.xml includes new page type
- [ ] llms.txt updated if new section added (cross-reference `geo-llm-optimizer.md`)
- [ ] Internal links: page is reachable within 2 clicks from homepage
- [ ] Related content links present (RelatedEvents component)
- [ ] Lighthouse score ≥ 90 (Performance, Accessibility, Best Practices, SEO)
- [ ] No broken links
- [ ] Google Search Console: submit URL for indexing after deploy
