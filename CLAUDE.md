# NovaKidLife — Claude Code Project Guide

## Project Overview

**NovaKidLife** (novakidlife.com) is a family events discovery platform for Northern Virginia.
Live monetized business + AWS portfolio project. Built across 12 Claude Code sessions.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15.5.12 (static export) + TypeScript + Tailwind CSS 3.4 |
| Hosting | AWS S3 + CloudFront |
| API | AWS API Gateway + Lambda (Python 3.12) |
| Database | Supabase (PostgreSQL + pgvector) — local Docker in dev, cloud at launch |
| Queue | AWS SQS + DLQ |
| Scheduler | AWS EventBridge |
| AI | OpenAI gpt-4o-mini (extraction + alt text) + Imagen 3 / DALL-E 3 (images) |
| Social | Buffer API |
| IaC | Terraform (S3 backend, DynamoDB lock) |
| CI/CD | GitHub Actions (5 workflows incl. Lighthouse CI) |

---

## Repository Structure

```
novakidlife/
├── .github/workflows/            # 5 GitHub Actions workflows
├── apps/
│   └── web/                      # Next.js 15 frontend
│       ├── public/fonts/
│       ├── scripts/
│       │   └── download-fonts.mjs  # Node.js font downloader (cross-platform)
│       ├── src/
│       │   ├── app/              # App Router pages + layouts
│       │   ├── components/       # Reusable UI components
│       │   ├── fonts/            # Self-hosted woff2 files
│       │   ├── lib/              # fonts.ts, api.ts, utilities
│       │   └── types/            # supabase.ts (generated)
│       ├── next.config.js        # output: 'export', trailingSlash: true
│       ├── tailwind.config.ts
│       └── tsconfig.json
├── docs/                         # Dev log, architecture, ADRs, SEO log, etc.
├── infra/terraform/              # Terraform IaC
├── services/
│   ├── api/                      # Main REST API Lambda (Python)
│   ├── events-scraper/           # 3-tier scraping Lambda (Python)
│   │   ├── scrapers/
│   │   │   ├── base.py           # BaseScraper (httpx, retry, HTML clean)
│   │   │   ├── models.py         # RawEvent, EventType, DealCategory
│   │   │   ├── publisher.py      # SQS batch publisher
│   │   │   ├── tier1/            # Library APIs, Eventbrite
│   │   │   ├── tier2/            # AI extractor (gpt-4o-mini, config-driven)
│   │   │   ├── tier3/            # Deal monitors (KrazyCouponLady, Hip2Save, Google News RSS)
│   │   │   └── pokemon/          # Pokémon TCG events + product drops
│   │   └── config/sources.json   # All scrape sources (add Tier 2 here, zero code)
│   ├── image-gen/                # AI image generation Lambda (Python)
│   │   ├── prompts.py            # Prompt library (WEBSITE_PROMPTS, SOCIAL_PROMPTS, POKEMON_PROMPTS)
│   │   ├── sourcer.py            # Scraped URL → Google Places → None
│   │   ├── generator.py          # Imagen 3 primary, DALL-E 3 fallback
│   │   ├── enhancer.py           # Pillow warm color grade
│   │   ├── processor.py          # Resize, WebP, LQIP, blurhash
│   │   ├── alt_text.py           # gpt-4o-mini SEO alt text
│   │   └── uploader.py           # S3 + CDN URLs
│   ├── scheduler/                # EventBridge trigger stub
│   └── social-poster/            # Buffer API Lambda (Python)
│       ├── handler.py            # EventBridge-triggered Lambda entry point
│       ├── buffer_client.py      # Buffer API v1 wrapper (Platform enum, BufferClient)
│       ├── copy_builder.py       # Platform-specific copy: Twitter/Instagram/Facebook
│       ├── scheduler.py          # Optimal posting slot calculator (Eastern timezone)
│       ├── ssm.py                # SSM parameter helper with .env fallback
│       └── tests/                # pytest: test_copy_builder.py, test_scheduler.py
├── supabase/
│   └── migrations/               # 11 migration files (see Database Schema below)
├── skills/                       # Claude Code operational runbooks
├── CLAUDE.md                     # This file
└── package.json                  # npm workspaces root
```

---

## Database Schema

**Local Supabase via Docker** (ADR-008). Run: `supabase start`
Studio at: http://127.0.0.1:54323

### Tables

| Table | Key Columns |
|-------|------------|
| `events` | id, slug, title, short_description, full_description, start_at, end_at, venue_name, address, location_text, location_id, lat, lng, tags[], event_type, section, brand, image_url, image_url_md, image_url_sm, og_image_url, social_image_url, image_alt, image_blurhash, image_width, image_height, social_posted_platforms[], social_posted_at, embedding (vector) |
| `categories` | id, name, slug (15 seeded) |
| `locations` | id, name, slug, lat, lng (15 NoVa locations seeded) |
| `newsletter_subs` | id, email, created_at |

> **DB ↔ API column name mapping:** The DB uses `venue_name` / `address` / `full_description`, but the API response (and TypeScript types) expose them as `location_name` / `location_address` / `description`. The `event_to_response()` function in `services/api/models.py` must handle this mapping — verify when wiring end-to-end.

### Event Types (`event_type` column)
- `event` — standard family event
- `deal` — restaurant/activity deal
- `birthday_freebie` — free birthday offers
- `amusement` — amusement park deals
- `seasonal` — holiday/seasonal events
- `pokemon_tcg` — Pokémon TCG leagues, prereleases, tournaments
- `product_drop` — new Pokémon TCG set releases with retailer matrix

### Site Sections (`section` column)
- `main` — primary events feed at `/events`
- `pokemon` — Pokémon TCG hub at `/pokemon`

### Migrations (applied in order)
```
20260313000001  pgvector + uuid-ossp extensions
20260313000002  locations table (15 NoVa locations)
20260313000003  categories table (15 categories)
20260313000004  events table (34 cols, RLS, indexes, ivfflat)
20260313000005  newsletter_subs table
20260313000006  fix newsletter RLS (email regex)
20260314000001  deal fields (event_type, brand, discount_description, deal_category)
20260314000002  image SEO fields (alt, width, height, blurhash, url_md, url_sm, social_url, og_url)
20260314000003  section field (routes events to site sections)
20260314000004  search_events() pgvector RPC (cosine similarity, OPERATOR(extensions.<=>) syntax)
20260314000005  fix event_type constraint (adds pokemon_tcg + product_drop values)
20260315000001  social tracking (social_posted_platforms text[], social_posted_at timestamptz)
```

Run migrations: `supabase migration up`
Regenerate types: `supabase gen types typescript --local | Out-File -FilePath apps/web/src/types/supabase.ts -Encoding UTF8`

---

## Scraper Architecture (3-tier + Pokémon)

```
EventBridge (daily 6am EST)
    │
    ▼
events-scraper Lambda
    │
    ├── Tier 1 (structured)     5 sources — Fairfax/Loudoun/Arlington libraries, Eventbrite NoVa, Meetup API
    │     LibCal API → JSON-LD → AI fallback cascade
    │
    ├── Tier 2 (AI-extracted)   46 sources — config-driven, zero code per source
    │     URL → clean HTML → gpt-4o-mini → RawEvent[]
    │     Add new source: 1 JSON entry in config/sources.json
    │
    ├── Tier 3 (deal monitors)  5 sources
    │     KrazyCouponLady, Hip2Save (AI HTML extraction)
    │     Google News RSS (viral deals + birthday freebies + amusement)
    │
    └── Pokémon TCG section     3 sources
          Play! Pokémon event locator (15 NoVa zip codes)
          5 NoVa LGS websites (Nerd Rage Gaming, Battlegrounds, etc.)
          Google News RSS (restocks, prereleases, drops)
    │
    ▼
SQS Queue: novakidlife-events-queue
    │
    ├── image-gen Lambda        (sourcer → generator → enhancer → processor → upload)
    └── Supabase events table
```

---

## Image Generation Pipeline

**Two distinct pipelines** — website and social are always generated separately.

```
Event row
    │
    ├── Website image (16:9)
    │     sourcer.py      scraped URL → Google Places → None
    │     generator.py    Imagen 3 → DALL-E 3 fallback
    │     enhancer.py     Pillow warm grade (amber-leaning, no cold blues)
    │     processor.py    hero 1200×675, hero-md 800×450, hero-sm 400×225,
    │                     card 600×400, og 1200×630, LQIP 20×11, blurhash
    │
    └── Social image (1:1)    ← always AI-generated, never sourced
          generator.py    flat editorial illustration prompt
          processor.py    social 1080×1080
    │
    alt_text.py           gpt-4o-mini → ≤125 char SEO alt text
    uploader.py           S3 events/{slug}/*.webp, 1-year cache headers
    Supabase PATCH        all 10 image columns updated
```

### Prompt Libraries (`services/image-gen/prompts.py`)
- `WEBSITE_PROMPTS` — 14 keys, photorealistic editorial photography style
- `SOCIAL_PROMPTS` — 14 keys, flat editorial illustration style
- `POKEMON_PROMPTS` — 7 keys, TCG-specific (league/prerelease/regional/drops)

Pokémon events (`section = 'pokemon'`) automatically route to `POKEMON_PROMPTS`.

### S3 Path Convention
```
events/{slug}/hero.webp      1200×675   website hero
events/{slug}/hero-md.webp    800×450   srcset medium
events/{slug}/hero-sm.webp    400×225   srcset small
events/{slug}/card.webp       600×400   event card
events/{slug}/og.webp        1200×630   OpenGraph / Twitter card
events/{slug}/social.webp   1080×1080   social post
```
CDN base: `https://media.novakidlife.com`

---

## Pokémon TCG Section

Dedicated hub at `/pokemon` (separate from main `/events` feed).

**Sources:**
- `scrapers/pokemon/events_scraper.py` — Play! Pokémon locator + 5 NoVa LGS
- `scrapers/pokemon/drops_scraper.py` — release calendar + NoVa retailer matrix

**NoVa Retailer Matrix (15 stores in `drops_scraper.py`):**
- Big box: Target, Walmart, GameStop, Best Buy, Costco, Sam's Club, Five Below, Books-A-Million
- Specialty LGS: Nerd Rage Gaming (Manassas), Battlegrounds (Leesburg/Ashburn), The Game Parlor (Chantilly), Collector's Cache (Alexandria), Dream Wizards (Rockville MD)
- Online: TCGPlayer, Pokémon Center

Strategy: No real-time inventory scraping (too fragile). Each retailer entry has a direct product search URL + all NoVa store locations + buying tips.

---

## Frontend Pages

### App Router structure (`apps/web/src/app/`)
```
app/
├── layout.tsx                  # Root layout: fonts, global metadata (title template, twitter card)
├── page.tsx                    # Homepage (design system demo → replace at launch) + WebSite/LocalBusiness JSON-LD
├── globals.css                 # CSS custom properties (color tokens)
├── sitemap.ts                  # Dynamic sitemap.xml — fetches all slugs from /sitemap API
├── robots.ts                   # robots.txt — allows all + explicit AI bot list
├── events/
│   ├── page.tsx                # Events listing — server component, metadata, Suspense wrapper
│   ├── EventsClient.tsx        # 'use client' — URL-synced filters, search, pagination
│   └── [slug]/
│       └── page.tsx            # Event detail — generateStaticParams + generateMetadata + full SEO layout
└── public/
    └── llms.txt                # GEO file for LLM crawlers (site description, sections, data sources)
```

### Components (`apps/web/src/components/`)
| Component | Purpose |
|-----------|---------|
| `BlurImage` | LQIP blur-up, explicit width/height (CLS prevention) |
| `EventCard` | Article card with date, cost badge, tags, blur image |
| `EventCardSkeleton` / `EventGridSkeleton` | Pulse skeleton placeholders |
| `EventGrid` | Responsive 1→2→3 grid, priority LCP on first 3 |
| `SearchBar` | 500ms debounce, spinner, clear button |
| `FilterBar` | Date presets, category, free toggle, result count |
| `Pagination` | Ellipsis-aware page list, aria-current |
| `EmptyState` | No-results copy with clear filters CTA |
| `Breadcrumbs` | Nav with chevron separators, aria-current on last item |
| `EventJsonLd` | 3 JSON-LD scripts: Event + BreadcrumbList + FAQPage |
| `RelatedEvents` | Client-side fetch: 3 events by section + tags |
| `ShareButtons` | Copy link, Twitter/X intent, Facebook sharer |

### SEO conventions (see `skills/seo-geo.md` for full spec)
- Titles: `{Event} — {City}, VA` → template appends `| NovaKidLife` → final 50–60 chars
- Descriptions: `Day, Mon Date · Time at Location. Snippet. Cost.` → 140–155 chars
- `extractCity()` in `EventJsonLd.tsx` — parses city from address, falls back to "Northern Virginia"
- All event pages: Event + BreadcrumbList + FAQPage JSON-LD
- Homepage: WebSite (sitelinks searchbox) + LocalBusiness JSON-LD
- `generateStaticParams` returns `[]` gracefully if API is unavailable at build time

---

## Design System

### Colors
- **Primary**: Amber (`--color-primary-*`) — warm, family-friendly
- **Secondary**: Sage (`--color-secondary-*`) — natural, calming
- CSS custom properties in `apps/web/src/app/globals.css`
- Tailwind tokens hardcoded in `apps/web/tailwind.config.ts` (required for opacity modifiers)

### Typography
- **Headings/UI**: Nunito — weights 600, 700, 800 (`font-heading`)
- **Body**: Plus Jakarta Sans — weights 400, 500, 600 (`font-body`)
- Self-hosted via `next/font/local` — font files in `apps/web/src/fonts/`
- Download fonts (one-time): `node apps/web/scripts/download-fonts.mjs`

---

## Key Commands

```powershell
# Frontend development (PowerShell — use ; not &&)
cd apps/web
npm run dev           # start dev server (localhost:3000)
npm run build         # static export to out/
npm run type-check    # TypeScript check

# Download self-hosted fonts (one-time setup)
node apps/web/scripts/download-fonts.mjs

# Supabase (local Docker)
supabase start        # start local instance
supabase stop         # stop
supabase migration up # apply pending migrations
supabase db reset     # reset + replay all migrations

# Regenerate TypeScript types after schema changes
supabase gen types typescript --local | Out-File -FilePath apps/web/src/types/supabase.ts -Encoding UTF8

# Python services (run from service directory)
pip install -r requirements.txt
pytest tests/

# Terraform
cd infra/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

> **Windows note:** PowerShell does not support `&&`. Use `;` or run commands separately.

---

## Environment Variables

### `apps/web/.env.local`
```
NEXT_PUBLIC_API_URL=https://api.novakidlife.com
NEXT_PUBLIC_SITE_URL=https://novakidlife.com
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_...
```

### `services/*/` `.env` files (local dev)
```
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=sb_secret_...
OPENAI_API_KEY=
GOOGLE_PROJECT_ID=
GOOGLE_LOCATION=us-central1
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_PLACES_API_KEY=
MEDIA_BUCKET_NAME=novakidlife-media
MEDIA_CDN_URL=https://media.novakidlife.com
```

Python services use SSM Parameter Store in production (`/novakidlife/` prefix).

---

## Conventions

### Frontend
- Named exports only (except `page.tsx` / `layout.tsx`)
- Client components: `'use client'` only when genuinely needed
- Components: PascalCase `.tsx` in `src/components/`
- API client: `src/lib/api.ts`

### Python Services
- Lambda entry point always `handler.py` at service root
- Shared DB client: `services/api/db.py` (cached Supabase client)
- Tests: `tests/` with pytest
- Linting: ruff

### Database
- pgvector in `extensions` schema — column type `extensions.vector(1536)`
- Triggers use `security definer set search_path = ''`
- `supabase migration up` for local (not `db push` — requires linked remote)
- Supabase CLI v2 keys: `sb_publishable_*` (anon) / `sb_secret_*` (service)

### Terraform
- All resources tagged: `project=novakidlife`, `env=prod`
- State: S3 `novakidlife-tfstate`, DynamoDB `novakidlife-tflock`
- Never `apply` without reviewing `plan` output first

### Git
- Branch: `main` (direct commits, solo project)
- Commit prefix: `feat:`, `fix:`, `infra:`, `chore:`

---

## Session Roadmap

| Session | Focus | Status |
|---------|-------|--------|
| 1 | Foundation: repo, Next.js 15, design system, 15 skills | ✅ |
| 2 | Database: Supabase schema, migrations, pgvector | ✅ |
| 3 | Events Scraper: 3-tier (59 sources, deals, AI extraction) | ✅ |
| 4 | Image Gen: two pipelines, WebP variants, LQIP, SEO alt text | ✅ |
| 4b | Pokémon TCG section: scrapers, retailer matrix, prompts | ✅ |
| 5 | API: 15 REST endpoints + pgvector search | ✅ |
| 6 | Frontend: Events listing page (8 components, URL-synced filters) | ✅ |
| 7 | Frontend: Event detail page + SEO/GEO infrastructure | ✅ |
| 8 | Social Poster: Buffer API Lambda | ✅ |
| 9 | Terraform: Full IaC for all resources | ⬜ |
| 10 | CI/CD: 5 GitHub Actions workflows | ⬜ |
| 11 | SEO + Performance: Lighthouse 90+, sitemaps, structured data | ⬜ |
| 12 | Launch: monitoring, alerting, DNS, go-live | ⬜ |

---

## Skills Reference

Operational runbooks in `/skills/`:
- `deploy-frontend.md` — S3 deploy + CloudFront invalidation
- `deploy-api.md` — Lambda package + publish
- `db-migrate.md` — Supabase migrations
- `add-component.md` — React component scaffolding
- `add-lambda.md` — Lambda function scaffolding
- `generate-event.md` — AI event generation
- `generate-image.md` — Full image pipeline (source → grade → variants → upload)
- `post-social.md` — Buffer API posting
- `scrape-events.md` — Trigger + monitor scraper (all tiers)
- `terraform-plan.md` — Safe Terraform plan
- `terraform-apply.md` — Gated Terraform apply
- `seed-db.md` — Seed Supabase with test data
- `test-api.md` — API endpoint testing
- `check-lighthouse.md` — Lighthouse CI
- `monitor.md` — System health checks
- `seo-geo.md` — **SEO + GEO standards** (title/description lengths, H1/H2/H3 hierarchy, JSON-LD schemas per page type, GEO platform table, llms.txt, Core Web Vitals targets, pre-ship checklist). **Apply on every session that touches frontend pages.**
- `social-strategy.md` — Platform-specific social strategy: Twitter/X algorithm optimization, Instagram, Facebook groups, hashtag playbook, content calendar, copy templates by event type
- `brand-voice.md` — NovaKidLife tone + voice rules, language dos/don'ts, visual identity, color usage, typography, user personas
- `content-generation.md` — Templates for all content types: event descriptions, short descriptions, meta descriptions, FAQ copy, social captions, weekly roundups, AI generation prompts
- `autonomous-agents.md` — Full autonomous operation architecture: scheduled triggers, event lifecycle, failure handling, DLQ strategy, human-in-the-loop touchpoints, future agent roadmap
- `mcp-builder.md` — Guide for building MCP servers: planned MCPs (events, admin, social), design principles, FastMCP patterns, when MCP vs Lambda vs skill
- `skill-creator.md` — How to create new skills: format, quality checklist, skill categories, step-by-step process

> **Master reference:** See `docs/system-map.md` for the complete bird's-eye view of the entire system — all files, data flows, configuration, and session roadmap in one place.
