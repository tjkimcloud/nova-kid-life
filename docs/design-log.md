# Design Log — NovaKidLife

Running record of design decisions with rationale. Updated each session.

---

## Color System

### Decision: Amber as Primary Brand Color
**Date:** 2026-03-13 | **Status:** Adopted

Amber (`#F59E0B` base, Tailwind amber scale) chosen as the primary brand color.

**Rationale:**
- Warm, optimistic, and energetic — emotionally right for a family/kids platform
- Stands apart from the blue/green sea of tech and event sites
- Strong contrast with white backgrounds at mid-tones (500–700) — accessibility-friendly
- Evokes sunshine, outdoor activities, and community warmth
- Works beautifully in photography contexts (golden hour, autumn festivals)

**Implementation:** Full 50–950 scale as CSS custom properties (`--color-primary-*`) and Tailwind tokens. Semantic token `--color-background` maps to `primary-50` for a warm off-white page background.

---

### Decision: Sage as Secondary Brand Color
**Date:** 2026-03-13 | **Status:** Adopted

Custom sage green scale (desaturated, warm-leaning green) as the secondary color.

**Rationale:**
- Complements amber on the warm side of the color wheel without clashing
- Evokes parks, nature, outdoor spaces — aligned with NoVa's suburban/outdoor culture
- Desaturated enough to function as a neutral for text and UI chrome
- Differentiates from the standard Tailwind green/emerald scales

**Implementation:** Custom 50–950 scale. Mid-tones (500–600) used for secondary text, tags, and accents. Light tones (50–100) used for subtle surface backgrounds.

---

## Typography

### Decision: Nunito for Headings and UI
**Date:** 2026-03-13 | **Status:** Adopted

**Rationale:**
- Rounded letterforms create an approachable, friendly personality
- Exceptionally legible at large display sizes (hero headings, event titles)
- Weight range (600–800) provides clear visual hierarchy without harsh contrast
- Popular in family/education contexts — subconscious trust signal for target audience
- Variable font available, but we use discrete weights to minimize file size

**Weights used:** 600 (SemiBold), 700 (Bold), 800 (ExtraBold)
**CSS variable:** `--font-nunito`, Tailwind class: `font-heading`

---

### Decision: Plus Jakarta Sans for Body Text
**Date:** 2026-03-13 | **Status:** Adopted

**Rationale:**
- Modern geometric sans-serif with warm humanist touches — pairs naturally with Nunito
- Excellent readability at small sizes (event descriptions, metadata, captions)
- Professional enough for parent-facing content (event times, addresses, costs)
- Distinguishes body from headings without jarring contrast

**Weights used:** 400 (Regular), 500 (Medium), 600 (SemiBold)
**CSS variable:** `--font-plus-jakarta`, Tailwind class: `font-body`

---

### Decision: Self-Hosted Fonts
**Date:** 2026-03-13 | **Status:** Adopted

Fonts served from our own CDN (CloudFront) rather than Google Fonts CDN.

**Rationale:**
- **Performance:** Eliminates cross-origin DNS lookup + connection overhead to fonts.googleapis.com
- **Privacy:** No user requests leave to Google — GDPR/CCPA cleaner
- **Reliability:** Not dependent on Google Fonts uptime
- **Lighthouse:** Self-hosted fonts score better on render-blocking resource audits
- **Control:** Exact woff2 files pinned — no surprise updates

**Implementation:** `next/font/local` with files in `src/fonts/`. Download script: `node apps/web/scripts/download-fonts.mjs`.

---

## Layout & Shape Language

### Decision: Rounded Corners (2xl / 3xl)
**Date:** 2026-03-13 | **Status:** Adopted

Cards, buttons, and containers use `rounded-2xl` (1rem) and `rounded-3xl` (1.5rem) by default.

**Rationale:**
- Softer, more welcoming aesthetic — appropriate for family and children's content
- Consistent with Nunito's rounded letterforms (shape language cohesion)
- Trend-aligned without being trendy (rounded corners have multi-year staying power)

---

### Decision: Mobile-First Layout
**Date:** 2026-03-13 | **Status:** Adopted

All components designed for mobile first, enhanced for tablet and desktop.

**Rationale:**
- Primary use case: parent on their phone searching "things to do this weekend"
- Google mobile-first indexing — mobile layout is what gets crawled/ranked
- Forces content prioritization — what matters most on a 375px screen?
- Tailwind's default breakpoint system (`sm:`, `md:`, `lg:`) supports mobile-first naturally

---

## Static Architecture

### Decision: Warm Off-White Background (`primary-50`)
**Date:** 2026-03-13 | **Status:** Adopted

Page background is `#FFFBEB` (amber-50) rather than pure white.

**Rationale:**
- Reduces eye strain for long browsing sessions
- Creates a cohesive warm brand feel — even empty pages feel on-brand
- Distinguishes white `surface` (cards, modals) from the page background without harsh contrast

---

## Homepage V2 — Airbnb-Style Layout
**Date:** 2026-03-18 | **Status:** Built (Sessions 13–15)

Replaced the original placeholder homepage with a full content-driven layout:

**Structure:**
1. `HeroSearch` — full-width hero with date/location/age pickers, quick-filter pills ("Free", "This Weekend", "Indoors"), week calendar strip, social proof counter
2. Dark stats bar — event count, source count, geographic coverage area
3. Category grid (6 emoji cards) — browse by type
4. `WeekendEventsSection` — Sat/Sun tab toggle, Editor's Pick badge, save buttons
5. Age group grid (4 cards: Babies, Toddlers, Elementary, Tweens+)
6. `FreeEventsSection` — SEO-targeted "Free Things To Do With Kids in NoVa"
7. `CityStripsSection` — 4 horizontal strips (Reston, Fairfax, Arlington, Leesburg)
8. Blog/editorial section (3 post cards from `/blog` API)
9. Coverage area pill links
10. Newsletter CTA

**Known issues after V2 launch (Session 18 feedback):**
- The layout still feels "directory-ish" — too many grids, too structured, not enough warmth
- Hero has no real photo — gradient only, feels generic
- Blog cards use emoji as image placeholder — breaks trust/quality perception
- First impression doesn't convey warmth, family joy, or community feel

---

## Homepage V3 — Warm Editorial Redesign (Planned)
**Date:** 2026-03-23 | **Status:** Planned

**Problem:** The current V2 homepage reads like a structured directory — useful but cold. The target audience (parents/caregivers) responds to warmth, community, and visual storytelling. A grid of event cards doesn't communicate "someone curated this for you."

**Design direction:**
- Hero: Full-bleed real family lifestyle photo (warm, candid, Northern Virginia settings — parks, farms, festivals). Text overlay: short emotional headline, single CTA. No search widget in the hero — move search lower.
- Lead with a featured blog post / editorial story (image + headline + lede paragraph) — makes the site feel like a magazine, not a directory.
- Reduce visual noise: fewer grids, more whitespace, let content breathe.
- Blog cards must have images (use event images or AI-generated editorial images, not emoji).
- City strips and category browsing stay — move them lower in the page hierarchy.
- SEO sections (FreeEventsSection) stay but are integrated more naturally into the editorial flow.

**Decision: Image strategy for blog posts**
Don't generate a unique AI image for every event — that's expensive and slows the pipeline. Instead:
- Blog post cards use the hero image from the first event in the post (already generated)
- If no event image, use a curated stock photo from the seasonal/topic pool
- Never use emoji or solid-color placeholders for blog cards — they signal low quality

**Inspiration:** Local magazine sites, Airbnb editorial, Patch.com at its best

---

## Future Design Decisions (TBD)

- [ ] Dark mode strategy (CSS var approach makes this straightforward later)
- [ ] Event card layout variants (list vs. grid vs. map)
- [ ] Image aspect ratio standard for event hero images (currently 16:9)
- [ ] Icon library selection
- [ ] Animation/transition library (Framer Motion vs. CSS transitions)
- [ ] Hero photo library — curated real NoVa family photos vs. stock (Unsplash NoVa collections)
