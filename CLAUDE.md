# NovaKidLife — Claude Code Project Guide

## Project Overview

**NovaKidLife** (novakidlife.com) is a family events discovery platform for Northern Virginia.
Live monetized business + AWS portfolio project. Built across 16 sessions and running autonomously.

**Site is LIVE** at https://novakidlife.com — CloudFront + ACM wildcard cert (`*.novakidlife.com`) + Route 53 DNS.
Supabase cloud project: `ovdnkgpdgkceulkpwedj` (linked via `supabase link --project-ref ovdnkgpdgkceulkpwedj`).

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
| Social | Ayrshare API (replaced Buffer — Buffer removed public API access for new users) |
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
│   │   ├── sourcer.py            # Scraped URL → Google Places → Unsplash → Pexels → None (AI fallback)
│   │   ├── generator.py          # Imagen 3 primary, DALL-E 3 fallback
│   │   ├── enhancer.py           # Pillow warm color grade
│   │   ├── processor.py          # Resize, WebP, LQIP, blurhash
│   │   ├── alt_text.py           # gpt-4o-mini SEO alt text
│   │   └── uploader.py           # S3 + CDN URLs
│   ├── content-generator/        # Blog post generation Lambda (Python)
│   │   ├── handler.py            # EventBridge-triggered (Thu 8pm + Mon 6am EST)
│   │   ├── post_builder.py       # 5 prompt builders (weekend/location/free/week-ahead/indoor)
│   │   ├── prompts.py            # 328-line prompt library with shared voice + FAQ rules
│   │   ├── github_trigger.py     # Triggers deploy-frontend workflow after new posts saved
│   │   ├── ssm.py                # SSM helper
│   │   └── tests/                # pytest: test_post_builder.py
│   ├── scheduler/                # EventBridge trigger stub
│   └── social-poster/            # Social poster Lambda (code exists, NOT deployed — removed from Terraform pending Ayrshare integration)
│       ├── handler.py            # EventBridge-triggered Lambda entry point
│       ├── buffer_client.py      # Buffer API v1 wrapper (Platform enum, BufferClient)
│       ├── copy_builder.py       # Platform-specific copy: Twitter/Instagram/Facebook
│       ├── scheduler.py          # Optimal posting slot calculator (Eastern timezone)
│       ├── ssm.py                # SSM parameter helper with .env fallback
│       └── tests/                # pytest: test_copy_builder.py, test_scheduler.py
├── supabase/
│   └── migrations/               # 12 migration files (see Database Schema below)
├── scripts/
│   └── deploy-lambdas.py         # Lambda build + deploy script (pip manylinux, zip, S3 for >50MB)
├── skills/                       # Claude Code operational runbooks
├── CLAUDE.md                     # This file
└── package.json                  # npm workspaces root
```

---

## Database Schema

**Local Supabase via Docker** (ADR-008). Run: `supabase start`
Studio at: http://127.0.0.1:54323
**Cloud project:** `ovdnkgpdgkceulkpwedj` — link with `supabase link --project-ref ovdnkgpdgkceulkpwedj`

### Tables

| Table | Key Columns |
|-------|------------|
| `events` | id, slug, title, short_description, full_description, start_at, end_at, venue_name, address, location_text, location_id, lat, lng, tags[], event_type, section, brand, image_url, image_url_md, image_url_sm, og_image_url, social_image_url, image_alt, image_blurhash, image_width, image_height, social_posted_platforms[], social_posted_at, embedding (vector) |
| `categories` | id, name, slug (15 seeded) |
| `locations` | id, name, slug, lat, lng (15 NoVa locations seeded) |
| `newsletter_subs` | id, email, created_at |

> **DB ↔ API column name mapping:** The DB uses `venue_name` / `address` / `full_description`; SELECT queries in `routes/events.py` and `routes/pokemon.py` must use these DB names. The `event_to_response()` function in `services/api/models.py` renames them for the frontend response (`location_name` / `location_address` / `description`).

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
20260318000001  blog_posts table (slug unique, post_type, trigger_type, content Markdown, event_ids uuid[], RLS, idempotency constraint)
```

Run migrations (local): `supabase migration up`
Run migrations (cloud): `supabase db push` (requires linked project)
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
    └── image-gen Lambda
          Step 0: upsert RawEvent → Supabase (on_conflict=source_url) → get DB slug/id
          Step 1–7: sourcer → generator → enhancer → processor → upload → Supabase PATCH
```

---

## Image Generation Pipeline

**Two distinct pipelines** — website and social are always generated separately.

```
SQS RawEvent payload
    │
    ├── Step 0: _upsert_event()  — INSERT/upsert into Supabase (on_conflict=source_url)
    │                              Maps RawEvent fields → DB column names (venue_name, address, full_description)
    │                              Returns DB row with assigned slug + id
    │
    ├── Website image (16:9)
    │     sourcer.py      scraped URL → Google Places → Unsplash API → Pexels API → None (AI fallback)
    │     generator.py    Imagen 3 → DALL-E 3 fallback (last resort only — free stock preferred)
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
├── page.tsx                    # Homepage V2 — Airbnb-style hero search, weekend events, age groups, free events, city strips, editorial blog
├── globals.css                 # CSS custom properties (color tokens)
├── error.tsx                   # App Router error boundary ('use client')
├── global-error.tsx            # Global error boundary — wraps root layout ('use client')
├── not-found.tsx               # 404 page — required for static export (prevents Pages Router fallback)
├── sitemap.ts                  # Dynamic sitemap.xml — fetches all slugs from /sitemap API
├── robots.ts                   # robots.txt — allows all + explicit AI bot list
├── about/
│   └── page.tsx                # E-E-A-T about page (mission, coverage, 59+ sources)
├── privacy-policy/
│   └── page.tsx                # Privacy policy (noindex)
├── pokemon/
│   └── page.tsx                # Pokémon TCG hub — event types, 5 LGS cards, retailer guide
├── events/
│   ├── page.tsx                # Events listing — server component, metadata, Suspense wrapper
│   ├── EventsClient.tsx        # 'use client' — URL-synced filters, search, pagination
│   └── [slug]/
│       └── page.tsx            # Event detail — generateStaticParams + generateMetadata + full SEO layout
├── blog/
│   ├── page.tsx                # Blog listing — server component, metadata, Suspense skeleton, PostCard grid
│   └── [slug]/
│       └── page.tsx            # Blog detail — Article + BreadcrumbList + Event JSON-LD; Markdown renderer; EventCard grid
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
| `Header` | Sticky top nav — logo, Events + Pokémon TCG links, Find Events CTA |
| `Footer` | Dark sage — brand, social icons, coverage area, site links, copyright |
| `NewsletterForm` | `'use client'` — POSTs to `NEXT_PUBLIC_API_URL/newsletter/subscribe` |
| `HeroSearch` | `'use client'` — Airbnb-style search (location/date/age), quick filter pills, weekly calendar strip, social proof |
| `WeekendEventsSection` | `'use client'` — Sat/Sun tab toggle, ❤️ save buttons, ⭐ Editor's Pick badge |
| `FreeEventsSection` | Free events spotlight — SEO H2 "Free Things To Do With Kids in NoVa This Weekend" |
| `CityStripsSection` | 4 city strips (Reston, Fairfax, Arlington, Leesburg) — compact event lists with "See all" links |

### SEO conventions (see `skills/seo-geo.md` for full spec)
- Titles: `{Event} — {City}, VA` → template appends `| NovaKidLife` → final 50–60 chars
- Descriptions: `Day, Mon Date · Time at Location. Snippet. Cost.` → 140–155 chars
- `extractCity()` in `EventJsonLd.tsx` — parses city from address, falls back to "Northern Virginia"
- All event pages: Event + BreadcrumbList + FAQPage JSON-LD
- Homepage: WebSite (sitelinks searchbox) + LocalBusiness JSON-LD
- `generateStaticParams` returns `[{ slug: '_placeholder' }]` as fallback (NOT `[]` — Next.js 15 rejects empty arrays)
- All API fetches use `AbortSignal.timeout(8000)` to prevent build hangs when API is offline
- **Build quirk:** In some environments `npm run build` requires TWO passes — first pass may fail on Pages Router chunk resolution, second pass succeeds. Try single pass first; if it fails, run again without clearing `.next`. Documented in `skills/qa-build.md`.

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

# Lambda deployment (from repo root)
python scripts/deploy-lambdas.py api              # deploy API Lambda
python scripts/deploy-lambdas.py events-scraper   # deploy scraper
python scripts/deploy-lambdas.py image-gen        # deploy image-gen (uploads via S3 — package >50MB)
python scripts/deploy-lambdas.py api events-scraper image-gen content-generator  # deploy all four

# Terraform (MUST use default profile — novakidlife-dev used for state)
cd infra/terraform
$env:AWS_PROFILE="default"    # PowerShell — required, env has novakidlife profile by default
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
- All Lambda handlers call `_load_secrets_from_ssm()` at module init — env vars hold SSM paths (`*_PARAM`), not values
- SSM parameter prefix: `/novakidlife/` (e.g. `/novakidlife/openai/api-key`)
- Shared DB client: `services/api/db.py` (cached Supabase client)
- Tests: `tests/` with pytest
- Linting: ruff

### Database
- pgvector in `extensions` schema — column type `extensions.vector(1536)`
- Triggers use `security definer set search_path = ''`
- `supabase migration up` for local; `supabase db push` for cloud (requires linked project)
- Supabase CLI v2 keys: `sb_publishable_*` (anon) / `sb_secret_*` (service)
- Cloud project ID: `ovdnkgpdgkceulkpwedj`

### Terraform
- All resources tagged: `project=novakidlife`, `env=prod`
- State: S3 `novakidlife-tfstate`, DynamoDB `novakidlife-tflock`
- **Must use `AWS_PROFILE=default`** (TJ admin user) — shell default is `novakidlife` profile which lacks state permissions
- `terraform.tfvars` contains `web_acm_certificate_arn` (ACM cert ARN in us-east-1)
- Never `apply` without reviewing `plan` output first
- social-poster Lambda removed from Terraform (code in `services/social-poster/` is preserved)

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
| 8b | Blog / Content Generator: weekend roundups, SEO blog, 111 scrape sources | ✅ |
| 9 | Terraform: Full IaC for all resources | ✅ |
| 10 | CI/CD: 5 GitHub Actions workflows | ✅ |
| 11 | SEO + Performance: Lighthouse 90+, sitemaps, structured data | ✅ |
| 12 | Launch: Terraform IaC fixed, Route 53 DNS, ACM cert, Lambda deploy script, SSM secrets, DB migrations pushed to cloud, event pipeline fixed (upsert + column names), site LIVE | ✅ |
| 13 | Image sourcing expansion (Unsplash + Pexels), Homepage V2 components, API/Lambda SSM fixes, Terraform cleanup | ✅ |
| 14 | api.novakidlife.com DNS live, Lambda dependency deploys, GitHub token SSM, seasonal content generator (Easter/cherry blossom/spring), first scraper run | ✅ |
| 15 | CORS fix, image-gen pipeline fixes (slug + image_lqip column), homepage API wiring, scraper source fixes, frontend deployed | ✅ |
| 16 | Autonomy + Bug Fix | ✅ | Fixed localhost API URL in build, deleted stale events, daily auto-deploy cron, full docs refresh |

---

## Skill Library

All skills in `/skills/`. Archived (redistributed) skills in `/skills/archived/`.

### Operational SOPs

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `deploy-frontend.md` | deploy, S3, CloudFront | S3 deploy + CloudFront invalidation |
| `deploy-api.md` | deploy, Lambda, API | Lambda package + publish |
| `db-migrate.md` | migration, Supabase, schema | Supabase migrations |
| `add-component.md` | component, React, UI | React component scaffolding |
| `add-lambda.md` | Lambda, new service | Lambda function scaffolding |
| `generate-event.md` | event generation, AI | AI event generation |
| `generate-image.md` | image, WebP, LQIP, S3, pipeline | Image pipeline SOP — invocation, Lambda trigger, costs |
| `generate-image-source.md` | image sourcing, sourcer, Google Places, Unsplash, Pexels, WEBSITE_PROMPTS, SOCIAL_PROMPTS | Image sourcing logic and all three prompt libraries |
| `post-social.md` | social post, Buffer, Ayrshare | Social posting via Ayrshare API |
| `scrape-events.md` | scraper, trigger, monitor, invocation | Trigger and monitor the scraper Lambda |
| `scraper-add-source.md` | add source, new scraper, sources.json, Tier 2, LGS, RawEvent | Add new event sources; RawEvent model; architecture |
| `terraform-plan.md` | terraform, plan, IaC | Safe Terraform plan |
| `terraform-apply.md` | terraform, apply | Gated Terraform apply |
| `seed-db.md` | seed, database, test data | Seed Supabase with test data |
| `test-api.md` | API test, endpoint | API endpoint testing |
| `check-lighthouse.md` | Lighthouse, performance, CI | Lighthouse CI |
| `monitor.md` | monitor, health, quick check | Full-system quick health check |
| `monitor-api.md` | API health, Lambda errors, Supabase health | API/Lambda/DB diagnostics |
| `monitor-infra.md` | SQS, DLQ, CloudFront, cost, dashboard | SQS, CloudFront, cost monitoring |
| `qa-build.md` | **build, npm run build, pre-commit, static export** | **Pre-build checklist. Run before every `npm run build`.** |
| `next-15-patterns.md` | generateStaticParams, params Promise, notFound, force-static, Next.js 15, TypeScript error | Next.js 15 static export gotchas and patterns reference |

### SEO — Technical

| Skill | Triggers | Reference files |
|-------|----------|----------------|
| `seo-technical.md` | title tag, meta description, H1, canonical, OG image, Core Web Vitals, Lighthouse, pre-ship, sitemap, robots.txt | — |
| `seo-schema.md` | JSON-LD, structured data, schema, rich results, FAQPage, Event schema, ItemList, LocalBusiness | — |
| `seo-title-optimizer.md` | headline, title, H1, click-through, title formula | `title-formulas.md` |

### SEO — Content Strategy

| Skill | Triggers | Reference files |
|-------|----------|----------------|
| `seo-content-strategy.md` | keyword, content plan, topic cluster, internal linking, E-E-A-T, pillar page, URL structure, competitive, search intent | — |
| `seo-content-writer.md` | body copy, article, blog post, content structure, long-form, roundup | `content-structure-templates.md` |

### SEO — Analytics & Measurement

| Skill | Triggers | Reference files |
|-------|----------|----------------|
| `seo-analytics.md` | analytics, Google Search Console, GA4, KPI, tracking, Lighthouse, CloudWatch, metrics | — |

### GEO — LLM Optimization ⭐ Highest Priority

| Skill | Triggers | Reference files |
|-------|----------|----------------|
| `geo-llm-optimizer.md` | **LLM visibility, AI citation, Perplexity, ChatGPT, Claude, Gemini, Copilot, GEO, answer engine, llms.txt, AI search, generative engine** | `llm-citation-targets.md`, `geo-entity-definition.md`, `llms-txt-template.md` |

### Local SEO

| Skill | Triggers | Reference files |
|-------|----------|----------------|
| `local-seo-gbp.md` | Google Business Profile, GBP, photos, GBP posts, reviews, Q&A, Nextdoor, Facebook groups, local social, Instagram hashtags | — |
| `local-seo-citations.md` | citations, NAP, directories, Bing Places, Apple Maps, Yelp, BrightLocal, data aggregators, citation audit | — |
| `local-seo-content.md` | local link building, outreach, blog, location guide, seasonal guide, neighborhood, hyperlocal, near me, voice search, featured snippet, zero-click, landmark | — |
| `local-seo-schema.md` | GeoCoordinates, service area schema, areaServed, PostalAddress, GeoCircle, location page schema, Pokémon schema, ItemList location | — |
| `local-seo-tracking.md` | rank tracking, BrightLocal, citation audit, local SEO audit, launch timeline, GBP insights, Whitespark, monthly checklist | `local-seo-monthly-checklist.md` |

### Strategy & Architecture

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `social-strategy.md` | Twitter/X, Instagram, Facebook, content calendar, platform strategy | Platform decision guide + algorithm notes |
| `social-copy-templates.md` | social copy, caption, post template, copy formula, Twitter copy, Pokémon social | Ready-to-use copy templates by platform and event type |
| `social-hashtags.md` | hashtag, Instagram hashtags, Twitter hashtags, NoVa hashtags | Full hashtag library by category and platform |
| `brand-voice.md` | brand voice, tone, language, personas, visual identity | Core brand identity, voice attributes, language rules |
| `brand-voice-copy.md` | event description, short description, UI copy, error state, email subject | Event card copy rules, UI copy, email/newsletter copy |
| `brand-voice-blog.md` | blog voice, blog post, roundup, writing style, hook paragraph, sounds human | Blog + long-form editorial voice guide |
| `content-generation.md` | event description, FAQ copy, social captions, roundup | Content generation templates (all content types) |
| `autonomous-agents.md` | agent, autonomous, scheduler, DLQ, lifecycle | Full autonomous operation architecture |
| `mcp-builder.md` | MCP, Model Context Protocol, FastMCP | Guide for building MCP servers |
| `skill-creator.md` | new skill, skill format | How to create new skills |

### Archived (redistributed — do not use)
`skills/archived/seo-geo.md` — content fully redistributed into 5 focused SEO skills above
`skills/archived/local-seo.md` — content fully redistributed into 5 local-seo-* skills above

> **Master reference:** See `docs/system-map.md` for the complete bird's-eye view of the entire system — all files, data flows, configuration, and session roadmap in one place.

---

## Worktree Workflow

Three parallel worktrees for isolated feature development. Each maps to its own git branch.

| Worktree | Branch | Path | Purpose |
|----------|--------|------|---------|
| Main | `main` | `C:\Users\kimta\projects\nova-kid-life` | Production — deployments, hotfixes |
| Content | `feature-content` | `C:\Users\kimta\projects\nova-kid-life-content` | Blog, copy, SEO content work |
| Events | `feature-events` | `C:\Users\kimta\projects\nova-kid-life-events` | Scraper, image-gen, event pipeline |
| Infra | `feature-infra` | `C:\Users\kimta\projects\nova-kid-life-infra` | Terraform, Lambda, CI/CD |

### PowerShell Commands

```powershell
# Enter a worktree (open a new terminal in its directory)
Set-Location C:\Users\kimta\projects\nova-kid-life-content   # content work
Set-Location C:\Users\kimta\projects\nova-kid-life-events    # events pipeline
Set-Location C:\Users\kimta\projects\nova-kid-life-infra     # infra / Terraform

# Return to main worktree
Set-Location C:\Users\kimta\projects\nova-kid-life

# Check all worktrees and their HEAD commits
git worktree list

# After merging a feature branch, remove its worktree
git worktree remove C:\Users\kimta\projects\nova-kid-life-content
git worktree remove C:\Users\kimta\projects\nova-kid-life-events
git worktree remove C:\Users\kimta\projects\nova-kid-life-infra

# Merge a feature branch into main (run from main worktree)
git merge feature-content --no-ff -m "feat: merge feature-content"
git merge feature-events  --no-ff -m "feat: merge feature-events"
git merge feature-infra   --no-ff -m "feat: merge feature-infra"

# Re-create a worktree after removing it (e.g. to start a new feature cycle)
git worktree add ..\nova-kid-life-content -b feature-content
git worktree add ..\nova-kid-life-events  -b feature-events
git worktree add ..\nova-kid-life-infra   -b feature-infra

# See which branches have active worktrees
git worktree list --porcelain
```

### Rules
- Never commit directly to `main` from a feature worktree — open PRs or merge explicitly.
- Each worktree has its own working tree and index; changes in one do not bleed into others.
- `node_modules`, `.next`, and Python virtualenvs are **not** shared — install dependencies separately in each worktree if running dev servers there.
- Terraform state is shared (S3 backend) — only one worktree should run `terraform apply` at a time.
