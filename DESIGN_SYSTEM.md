# NovaKidLife — Design System
> **For Claude Code:** This file is the single source of truth for all visual design decisions on novakidlife.com. Apply these tokens, patterns, and rules to every component, page, and layout you build. Do not deviate without explicit instruction.

---

## 1. Palette — "Creamsicle Modern"

| Token | Hex | Usage |
|---|---|---|
| `--bg` | `#FFF8F2` | Page background, hero, all sections |
| `--bg2` | `#F5EDE0` | Card footers, subtle dividers |
| `--bg3` | `#EDE0CF` | Deepest background tint |
| `--white` | `#FFFFFF` | Cards, search bar, nav |
| `--orange` | `#E85D1A` | Primary CTA, active states, brand accent |
| `--orange-soft` | `#FF8C55` | Hover glow, underline accents |
| `--orange-pale` | `#FFF0E6` | Tag backgrounds, pill fills, newsletter bg |
| `--text` | `#1C1714` | All body text, headings |
| `--text2` | `#6B5E54` | Subtitles, descriptions, secondary copy |
| `--text3` | `#A89588` | Meta info, captions, placeholders |
| `--border` | `#EDE0CF` | All borders, dividers |
| `--green` | `#16A34A` | Success, free-event tag |
| `--green-pale` | `#DCFCE7` | Green tag background |
| `--blue` | `#1D4ED8` | STEM / info tags |
| `--blue-pale` | `#DBEAFE` | Blue tag background |
| `--yellow` | `#92400E` | Arts & crafts tag text |
| `--yellow-pale` | `#FEF3C7` | Yellow tag background |
| `--purple` | `#6D28D9` | Age/special tags |
| `--purple-pale` | `#EDE9FE` | Purple tag background |

**Rule:** Every section must have an explicit `background-color` set to a CSS variable — never rely on inheritance. This prevents dark mode bleed on iOS/Android.

---

## 2. Dark Mode — DISABLED

NovaKidLife is a light-only product. Apply the following to every page:

```css
html {
  color-scheme: light only;
  background: #FFF8F2 !important;
}
body {
  background: #FFF8F2 !important;
  color: #1C1714 !important;
}
* { color-scheme: light only; }
```

And always add explicit `background-color` to `.hero`, `.section`, `.footer`, `.nav`, `.search-wrap` — never leave them transparent.

---

## 3. Typography

### Font Stack
```css
/* Google Fonts import — always include this */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&display=swap');
```

| Role | Font | Weight | Notes |
|---|---|---|---|
| Display / Headings | `Plus Jakarta Sans` | 800 | All h1–h3, section titles, card titles, logo, stats |
| Body / UI | `DM Sans` | 400–600 | All body copy, labels, nav links, buttons, meta |

### Scale
| Element | Size | Weight | Letter-spacing |
|---|---|---|---|
| Hero h1 | `clamp(32px, 8vw, 52px)` | 800 | `-1px` |
| Section title | `19px` | 800 | `-0.3px` |
| Card title | `15px` (featured: `17px`) | 700 | `-0.1px` |
| Body / desc | `13–15px` | 400 | normal |
| Tags / labels | `10–11px` | 600 | `0.3px` |
| Meta / captions | `11–12px` | 400 | normal |
| Nav logo | `19px` (desktop: `21px`) | 800 | `-0.5px` |

**Rule:** Never use Inter, Roboto, Arial, system-ui, or Syne for headings. Always use Plus Jakarta Sans for display text.

---

## 4. Spacing & Radius

```css
--radius-sm:  10px;   /* buttons, inputs, small chips */
--radius:     16px;   /* age cards, city items */
--radius-lg:  22px;   /* event cards, newsletter */
```

| Context | Padding |
|---|---|
| Page sections | `40px 20px` (mobile) → `40px 32px` (desktop) |
| Nav height | `56px` mobile / `60px` desktop |
| Card body | `15px 16px 16px` |
| Card footer | `11px 16px` |
| Search bar | `14px 20px` |

---

## 5. Shadows

```css
--shadow-sm:     0 1px 4px rgba(0,0,0,0.06);      /* default card */
--shadow:        0 4px 20px rgba(0,0,0,0.08);      /* card hover */
--shadow-orange: 0 6px 20px rgba(232,93,26,0.28);  /* primary CTA button */
```

---

## 6. Components

### Buttons
```css
/* Primary */
.btn-orange {
  background: var(--orange); color: #fff;
  font-size: 14px; font-weight: 600;
  padding: 13px 22px; border-radius: var(--radius-sm);
  border: none; display: inline-flex; align-items: center; gap: 7px;
  box-shadow: var(--shadow-orange);
  transition: transform .15s, box-shadow .15s;
}
.btn-orange:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(232,93,26,0.35); }

/* Ghost */
.btn-ghost {
  background: var(--white); color: var(--text);
  font-size: 14px; font-weight: 500;
  padding: 12px 20px; border-radius: var(--radius-sm);
  border: 1.5px solid var(--border);
  display: inline-flex; align-items: center; gap: 7px;
  transition: border-color .15s, color .15s;
}
.btn-ghost:hover { border-color: var(--orange); color: var(--orange); }

/* Small (inside cards) */
.btn-xs {
  background: var(--orange); color: #fff;
  font-size: 12px; font-weight: 600;
  padding: 7px 14px; border-radius: 8px; border: none;
}
.btn-xs:hover { background: #D44E10; }
```

### Category Tags
```css
.tag { font-size: 10px; font-weight: 600; letter-spacing: 0.3px; padding: 3px 8px; border-radius: 6px; }
.tag-o  { background: var(--orange-pale); color: var(--orange); }   /* Arts, editor picks */
.tag-g  { background: var(--green-pale);  color: var(--green); }    /* Outdoors, Free */
.tag-b  { background: var(--blue-pale);   color: var(--blue); }     /* STEM, age ranges */
.tag-y  { background: var(--yellow-pale); color: var(--yellow); }   /* Arts & Crafts */
.tag-p  { background: var(--purple-pale); color: var(--purple); }   /* Special age/type */
```

### Nav
```css
.nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(255,248,242,0.95) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--border);
  height: 56px; /* 60px desktop */
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; /* 0 32px desktop */
}
```
- Logo: `Nova` (dark) + `Kid` (orange) + `Life` (dark) — always split this way
- Mobile: show logo + orange pill CTA only. Hide nav links.
- Desktop (768px+): show nav links + pill CTA

### Event Cards
- Border radius: `var(--radius-lg)` = 22px
- White background, `var(--border)` border
- Card image banner: 130px tall, emoji centered, gradient background
- Card body: tags → title → description → meta rows
- Card footer: separate `var(--bg)` background strip with price + small CTA button
- Hover: `translateY(-3px)` + elevated shadow
- Save button: absolute top-right, circular white button

### Featured Card
- Spans full grid width (`grid-column: 1 / -1`)
- Horizontal layout: 120px image column + content
- Slightly larger title (17px)

### Search Bar
- White background bar, full width
- Stacks vertically on mobile (field → chips row → full-width button)
- Goes horizontal row on 640px+
- Input: `var(--bg)` background, `var(--border)` border, focus → orange border

### Category Pills (horizontal scroll)
- `overflow-x: auto`, `scrollbar-width: none` — no scrollbar visible
- `flex-shrink: 0` on each pill — never wrap
- Active: orange fill. Hover: orange pale bg + orange border.

### Age Browse Grid
- 5 columns on mobile (repeat(5, 1fr))
- Cards: white bg, border, centered emoji + age range + count
- Hover: orange border + orange pale bg + emoji scale(1.15)

### City Tabs + List
- Tabs: horizontal scroll, active = dark (`var(--text)`) bg
- City items: white cards, orange-pale icon square, hover → orange border

### Newsletter
- Background: `var(--orange-pale)` — NOT dark/black
- Centered layout on mobile
- Pill-style email form: white background container, orange submit button fused to right
- Below form: fine print + benefit chips row

---

## 7. Layout Grid

```css
/* Section wrapper */
.section { padding: 40px 20px; background-color: var(--bg) !important; }
.section-inner { max-width: 900px; margin: 0 auto; }

/* Event cards */
mobile:  1 column (flex column)
560px+:  2 columns
900px+:  3 columns

/* City list */
mobile:  1 column
560px+:  2 columns

/* Blog cards */
mobile:  1 column
640px+:  3 columns
```

---

## 8. Mobile-First Rules

1. **Always design mobile layout first.** Add `@media(min-width: Npx)` breakpoints for desktop upgrades.
2. **Nav links hidden on mobile** — only logo + pill CTA visible.
3. **Horizontal scroll** for category pills and city tabs — never wrap or truncate.
4. **Full-width buttons** on mobile search bar — `width: 100%`, auto width on 640px+.
5. **Touch targets** minimum 44px height on all interactive elements.
6. **No hover-only interactions** — all states must work without hover.
7. **Sticky nav** with `backdrop-filter: blur(14px)` for depth on scroll.

---

## 9. Animations

Keep animations subtle and purposeful — not decorative noise.

```css
/* Fade up on load — use on major sections */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Blinking dot — hero eyebrow only */
@keyframes blink {
  0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
}

/* Card hover */
.card:hover { transform: translateY(-3px); box-shadow: var(--shadow); }

/* Button hover */
.btn-orange:hover { transform: translateY(-2px); }
```

---

## 10. Hero Pattern

The hero always follows this structure:
1. Eyebrow pill (blinking dot + uppercase label, orange-pale bg)
2. h1 with `"fun"` highlighted in orange with soft underline stroke
3. Subtitle paragraph (text2 color, max-width 480px)
4. Two CTAs: primary (orange) + ghost (white/border)
5. Stats row (3 stats, separated by top border)

```html
<!-- Hero eyebrow structure -->
<div class="hero-eyebrow">
  <span class="hero-dot"></span>
  Northern Virginia's #1 family guide
</div>

<!-- h1 accent pattern -->
<h1>Find something <span class="accent">fun</span> to do this weekend.</h1>
```

```css
.hero h1 .accent {
  color: var(--orange); position: relative; display: inline-block;
}
.hero h1 .accent::after {
  content: ''; position: absolute; left: 0; right: 0; bottom: 3px;
  height: 5px; background: var(--orange-soft); border-radius: 3px; opacity: 0.35;
}
```

---

## 11. What NOT to Do

- ❌ Never use dark backgrounds (`#1C1714`, `#111`, black) on any page section — only inside the newsletter card
- ❌ Never use Inter, Roboto, Arial, or system-ui fonts
- ❌ Never use amber or sage green — those are the old palette, fully retired
- ❌ Never rely on CSS inheritance for background colors — always set explicitly
- ❌ Never let dark mode override styles — `color-scheme: light only` must be on both `html` and `*`
- ❌ Never use purple gradients, generic card shadows, or bootstrap-style layouts
- ❌ Never wrap category pills or city tabs — always horizontal scroll

---

## 12. Reference File

The approved reference implementation is `novakidlife-v2.html`. When in doubt about any pattern, refer to that file. All future components should visually match the system defined there.
