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

## Future Design Decisions (TBD)

- [ ] Dark mode strategy (CSS var approach makes this straightforward later)
- [ ] Event card layout variants (list vs. grid vs. map)
- [ ] Image aspect ratio standard for event hero images (currently 16:9)
- [ ] Icon library selection
- [ ] Animation/transition library (Framer Motion vs. CSS transitions)
