# Dev Log — NovaKidLife

---

## Session 1 — 2026-03-13
**Theme:** Foundation — repo structure, design system, Next.js 14 setup

### What Was Built

**Repository scaffolding**
- Root npm workspaces (`apps/*`, `services/*`)
- `.gitignore` covering Node, Python, Terraform, AWS, OS artifacts
- `CLAUDE.md` — full project bible for all 12 sessions (stack, conventions, commands, session roadmap)

**Skill files (15)** — operational runbooks in `/skills/`:
`deploy-frontend`, `deploy-api`, `db-migrate`, `add-component`, `add-lambda`,
`generate-event`, `generate-image`, `post-social`, `scrape-events`,
`terraform-plan`, `terraform-apply`, `seed-db`, `test-api`, `check-lighthouse`, `monitor`

**Next.js 14 app (`apps/web/`)**
- Static export config (`output: 'export'`, `trailingSlash: true`)
- TypeScript strict mode, path alias `@/*` → `src/*`
- Tailwind CSS 3.4 + PostCSS + Autoprefixer

**Design system**
- Amber primary (50–950) + Sage secondary (50–950) — both as CSS custom properties and Tailwind color tokens
- Semantic tokens: `--color-background`, `--color-surface`, `--color-text-primary`, `--color-border`
- `next/font/local` config for Nunito (600/700/800) and Plus Jakarta Sans (400/500/600)
- Font download script: `node apps/web/scripts/download-fonts.mjs`
- Home page renders color swatches + type specimen for visual verification

**Service stubs**
- `services/api/`, `events-scraper/`, `image-gen/`, `social-poster/`, `scheduler/` — each with `package.json` npm scripts (test, lint, format, package, invoke, logs)

**Skeleton directories**
- `apps/web/src/components/`, `src/types/`, `src/fonts/`, `public/fonts/`
- `infra/terraform/`
- `.github/workflows/`

### Session Complete ✅
- npm resolved Next.js to **15.5.12** (newer than pinned 14.2.29 — compatible, no issues)
- Fonts downloaded successfully via `node apps/web/scripts/download-fonts.mjs`
- `npm run dev` confirmed — color swatches + type specimen visible at localhost:3000
- Note: PowerShell does not support `&&` — use `;` or run commands separately

### Files Created This Session
38 files total — see `docs/progress.md` for full checklist.

---

## Session 8 — 2026-03-15
**Theme:** Social Poster — Buffer API Lambda

### What Was Built

**DB migration** (`supabase/migrations/20260315000001_add_social_tracking.sql`)
- `social_posted_platforms text[] default '{}'` — tracks which platforms have been posted
- `social_posted_at timestamptz` — timestamp of most recent post
- GIN index on `social_posted_platforms` for fast unposted-event queries

**Buffer API wrapper** (`services/social-poster/buffer_client.py`)
- `Platform` enum: TWITTER, INSTAGRAM, FACEBOOK
- `BufferClient` — `get_profiles()`, `get_profiles_by_platform()`, `create_update()`, `get_pending_updates()`
- `BufferProfile` + `BufferUpdate` dataclasses

**Optimal posting scheduler** (`services/social-poster/scheduler.py`)
- `next_optimal_slot(after=None)` — finds next slot in Eastern timezone
  - Weekday: 9am, 12pm, 5pm ET
  - Weekend: 10am, 2pm ET
  - Quiet hours: 10pm–7am ET (skipped)
- `slots_for_week(start=None)` — returns all slots for a 7-day window
- `is_quiet_hours(dt)` — hour range check

**Platform-specific copy builder** (`services/social-poster/copy_builder.py`)
- `build_copy(event, platform)` — dispatches by platform
- Twitter (`_build_twitter`): 280 char limit, t.co link = 23 chars, 2–3 hashtags, emoji prefix by event type, free/cost indicator, Pokémon URL uses `/pokemon/events/` path
- Instagram (`_build_instagram`): 📅/⏰/📍 emoji detail cards, "Link in bio" CTA, 10–15 hashtag block, free events get `#FreeKidsEvents`
- Facebook (`_build_facebook`): full address, medium length, 1–2 hashtags, cost details
- `image_url_for_platform()` — Instagram → `social_image_url` (1080×1080); Twitter/Facebook → `og_image_url` (1200×630); falls back to `image_url`
- Full hashtag library: `#NoVaKids`, `#FamilyFun`, city tags (Fairfax/Reston/Chantilly/Loudoun/Manassas), event tags, seasonal, `#PokemonTCG`

**Lambda handler** (`services/social-poster/handler.py`)
- EventBridge-triggered (schedule, not SQS) — natural posting cadence control
- `_get_unposted_events()` — queries Supabase for published events not yet posted to a given platform
- `_normalize_event()` — maps DB column names to API field names
- `_mark_posted()` — appends platform slug to `social_posted_platforms` array
- `_process_platform()` — loops all pending events for one platform
- MAX_EVENTS_PER_RUN = 5 (Buffer API rate limit headroom)
- Supports `dry_run=True` and `platforms` filter in invocation payload
- SSM parameter fallback to local `.env`

**Tests**
- `tests/test_copy_builder.py` — 20+ tests: char limits, URL presence, hashtag presence, free/cost indicators, platform routing, Pokémon hashtags + URL path, deal copy, image URL fallbacks
- `tests/test_scheduler.py` — 15+ tests: future datetime, timezone-aware slot, not in quiet hours, valid slot hours, consecutive slots differ, after-parameter, weekday/weekend routing

**New skills (6)**
- `skills/social-strategy.md` — Twitter algorithm (Real-graph, SimClusters, TwHIN), Instagram content pillars, Facebook groups, weekly content calendar, copy templates per event type
- `skills/brand-voice.md` — voice attributes, tone by context, language rules (always/never say), two user personas (Busy Parent Beth, Pokémon Dad Dave), content quality checklist
- `skills/content-generation.md` — event descriptions (answer-first), short descriptions, meta descriptions, FAQ Q&As, social captions per platform, AI prompt library for Lambda enrichment
- `skills/autonomous-agents.md` — full architecture diagram, EventBridge schedules, 5-step event lifecycle, SQS/DLQ failure handling, CloudWatch alarms
- `skills/mcp-builder.md` — 3 planned MCPs (events, admin, social), FastMCP patterns
- `skills/skill-creator.md` — skill format spec, quality checklist, 6-step creation process

### Architecture Decision
EventBridge-triggered (not SQS-triggered) — posting time is about scheduling, not message processing. The Lambda runs on a cron, queries DB for all unposted events, and batches them intelligently. SQS would fire immediately on event creation, which is wrong for social media posting cadence.

### Session Complete ✅
Run `supabase migration up` to apply `20260315000001_add_social_tracking.sql`.

---

## Session 7 — 2026-03-14
**Theme:** Frontend — Event detail page + SEO/GEO infrastructure

### What Was Built

**Components (4)**
- `EventJsonLd` — renders 3 `<script type="application/ld+json">` tags: Event schema (with offers, isAccessibleForFree, eventStatus, location), BreadcrumbList, FAQPage (4 AI-generated Q&As from event data). Exports `extractCity()` helper (regex parses city from address, falls back to "Northern Virginia")
- `Breadcrumbs` — nav with chevron separators, aria-current on last item, truncation on long event titles
- `RelatedEvents` — 'use client', fetches events by section + tags on mount, filters out current event, shows 3 cards with skeleton loading
- `ShareButtons` — 'use client', copy-to-clipboard (2s feedback), Twitter/X share intent, Facebook sharer

**Event detail page** (`app/events/[slug]/page.tsx`)
- `generateStaticParams` → calls `/sitemap` API, returns main-section slugs; gracefully returns `[]` if API unavailable at build time
- `generateMetadata` → formats title to `{Event} — {City}, VA` (template appends `| NovaKidLife`); meta description `Day, Mon Date · Time at Location. Snippet. Cost.` trimmed to ≤155 chars
- H1/H2/H3 hierarchy per SEO+GEO spec: H1=title, H2=About/Details/Register/FAQ/Related
- Hero image: BlurImage with `priority=true` (LCP), explicit width/height from DB columns
- Event details: 4 icon cards (date/time, location, age range, cost) + Google Maps link
- How to Register section: only rendered when `registration_url` exists
- Visible FAQ section: 4 Q&A pairs for Google featured snippets + AI systems
- Share buttons + back-to-listing nav

**SEO + GEO infrastructure**
- `src/app/sitemap.ts` — dynamic sitemap fetches all slugs from API; static pages (priority 1.0/0.8) + event pages (0.6, weekly); graceful fallback to static-only if API unavailable
- `src/app/robots.ts` — allows all crawlers; explicitly lists GPTBot, PerplexityBot, ClaudeBot, Bingbot, Googlebot, OAI-SearchBot, cohere-ai
- `public/llms.txt` — LLM crawler file describing site, 7 content categories, geographic coverage, all 59 data sources, structured data summary
- `src/app/page.tsx` — WebSite schema (Google sitelinks searchbox via potentialAction) + LocalBusiness schema (4 NoVa county areaServed)
- `src/app/events/page.tsx` — meta description trimmed from 169→143 chars

### Session Complete ✅

---

## Session 6 — 2026-03-14
**Theme:** Frontend — Events listing page

### What Was Built

**Types + API client**
- `src/types/events.ts` — full TypeScript interfaces for Event, Category, Location, EventsResponse, EventsParams, EventType union
- `src/lib/api.ts` — typed API client with generic `apiFetch`, `buildQuery` helper, all endpoints covered

**Components (8)**
- `BlurImage` — blur-up placeholder using LQIP data URL as CSS background, fades in full WebP on load. Explicit width/height via padding-bottom prevents CLS
- `EventCard` — `<article>` with blur image, date/time formatted with Intl API (no library), title 2-line clamp, location pin SVG, cost badge (FREE/price), tag chips (max 3)
- `EventCardSkeleton` + `EventGridSkeleton` — Tailwind `animate-pulse` placeholders matching card layout
- `EventGrid` — 1→2→3 responsive CSS grid, priority prop on first 3 cards (LCP optimization)
- `SearchBar` — 500ms debounce, spinner on search, clear X button, accessible label
- `FilterBar` — date presets with computed date ranges (Today/Weekend/Week/Month), category select from API, Free toggle, result count, Clear all. `getDateRange()` exported for use in EventsClient
- `Pagination` — ellipsis-aware page list (shows max 7 pages), prev/next with aria
- `EmptyState` — different copy for "no results" vs "no filters matched"

**Page**
- `app/events/page.tsx` — server component for metadata (SEO title, OG, canonical), wraps `<Suspense>` with skeleton fallback
- `app/events/EventsClient.tsx` — 'use client', URL-synced state via `router.replace` + `useSearchParams`. Two fetch paths: semantic search (POST /events/search) for text queries, standard filter path (GET /events) for filter-only. Filters + page + query all serialized to URL params (shareable, bookmarkable).

### Architecture Notes
- `output: 'export'` (static build) → all data fetching is client-side. No RSC data fetching.
- `useSearchParams` inside a `<Suspense>` boundary (required by Next.js for static export)
- URL state: `?q=stem+for+kids&date=weekend&category=outdoor&free=true&page=2`

### Session Complete ✅

---

## Session 5 — 2026-03-14
**Theme:** API Lambda — 15 REST endpoints

### What Was Built

**Router** (`services/api/router.py`)
- Lightweight Lambda proxy integration router — no FastAPI dependency
- Path parameter extraction (`/events/{slug}` → `pathParameters.slug`)
- CORS headers on every response (`Access-Control-Allow-Origin: https://www.novakidlife.com`)
- OPTIONS preflight handler (204)
- Automatic 500 catch with logging

**Models** (`services/api/models.py`)
- `SearchRequest` — validates query (non-empty, ≤500 chars), clamps limit (1–50)
- `NewsletterSubscribeRequest` — Pydantic EmailStr validation
- `event_to_response()` — strips embedding vector before sending to frontend
- `paginated()` — consistent pagination envelope (`items`, `total`, `limit`, `offset`, `has_more`)

**Routes** (`services/api/routes/`)
- `events.py`:
  - `GET /events` — 7 filters: section, event_type, category, location_id, start_date, end_date, tags, is_free
  - `GET /events/featured` — `is_featured=true` events
  - `GET /events/upcoming` — next 7 days window
  - `GET /events/{slug}` — full event detail with joined categories + locations
  - `POST /events/search` — text → OpenAI embedding → pgvector cosine similarity via `search_events()` RPC
- `pokemon.py`:
  - `GET /pokemon/events` — filterable by format tag (league/prerelease/regional/tournament)
  - `GET /pokemon/drops` — product drops with embedded retailer matrix
  - `GET /pokemon/retailers` — full 15-store NoVa matrix (type filter: big_box/specialty/online)
- `categories.py` — `GET /categories` with live event counts
- `locations.py` — `GET /locations` with live event counts
- `newsletter.py` — `POST /newsletter/subscribe` with email upsert
- `sitemap.py` — `GET /sitemap` returns slug arrays split by section for Next.js `generateStaticParams`
- `admin.py` — `POST /admin/events/trigger-scrape` (async Lambda invoke), `GET /admin/health/detailed` (DB counts + queue depths)

**Migration** (`supabase/migrations/20260314000004_add_search_rpc.sql`)
- `search_events()` RPC: takes `query_embedding vector(1536)`, `match_section text`, `match_count int`
- Returns events + similarity score ordered by cosine distance
- `security definer set search_path = ''` (passes Supabase linter)

**Tests** (`services/api/tests/test_router.py`) — 20 tests, no external calls

### Session Complete ✅
Run `supabase migration up` to apply the `search_events` RPC function.

---

## Session 4 — 2026-03-14
**Theme:** Image Generation — two-pipeline design (website photo-realism + social illustration)

### What Was Built

**DB migration** — `supabase/migrations/20260314000002_add_image_seo_fields.sql`
- 8 new columns: `image_alt`, `image_width`, `image_height`, `image_blurhash`,
  `image_url_md`, `image_url_sm`, `social_image_url`, `og_image_url`

**Image generation service** (`services/image-gen/`)
- `prompts.py` — prompt library: 14 event types × 2 styles
  - `WEBSITE_PROMPTS` — photorealistic editorial photography (warm golden hour)
  - `SOCIAL_PROMPTS` — flat editorial illustration (amber + sage vector art)
  - Tag-based prompt matching via `get_website_prompt()` / `get_social_prompt()`
- `sourcer.py` — find existing image before calling AI:
  1. Scraped `image_url` (most events have one)
  2. Google Places Photos API for known venues (pre-seeded Place IDs)
  3. Return `None` → triggers AI generation
- `generator.py` — AI image generation:
  - Imagen 3 via Vertex AI REST (primary, `aspectRatio` 16:9 or 1:1)
  - DALL-E 3 via OpenAI (fallback, HD quality, b64_json)
  - Returns raw bytes regardless of provider
- `enhancer.py` — Pillow warm color grade applied to all images:
  - Warmth: R×1.05, G×1.00, B×0.90 (amber-leaning, no cold blues)
  - Contrast ×1.12, Saturation ×1.10, Brightness ×1.03
  - Radial vignette (18% strength) for editorial look
- `processor.py` — all output variants via smart center-crop + WebP:
  - Website: hero 1200×675, hero-md 800×450, hero-sm 400×225, card 600×400
  - SEO: og 1200×630
  - Social: 1080×1080
  - LQIP: 20×11 base64 WebP data URL (blur-up placeholder)
  - Blurhash: 4×3 components (CSS placeholder before LQIP loads)
- `alt_text.py` — gpt-4o-mini generates ≤125 char SEO alt text per event
- `uploader.py` — S3 upload with:
  - `Cache-Control: public, max-age=31536000, immutable`
  - CDN path: `events/{slug}/hero.webp`, etc.
  - Skip-if-exists check (idempotent)
- `handler.py` — Lambda SQS trigger:
  - Full pipeline: source → generate → enhance → process → alt_text → upload → DB PATCH
  - Social illustration always AI-generated (no sourcing for social)
  - Supabase REST PATCH updates all 10 image columns

**Tests** — `tests/test_processor.py`
- 14 tests covering all size variants, WebP format, LQIP correctness, file size limits

### Design Decisions
- **Two pipelines**: website = real photo (sourced or AI), social = always AI illustration
  - Ensures website looks credible (real photos where possible)
  - Ensures social is always brand-consistent (never a random photo)
- **Warm grade on everything**: color cohesion across sourced photos + AI images
- **Blurhash + LQIP**: double-layer blur-up — blurhash first (pure CSS, instant),
  then LQIP base64 (visible detail, 20px), then full image
- **Google Places pre-seeded**: 8 known NoVa venues avoid API calls for common locations
- **Skip-if-exists**: Lambda is idempotent — safe to re-trigger without cost

### Session Complete ✅
All 9 source files + 2 test files written. Run `supabase migration up` to apply the new image column migration.

---

## Session 3 — 2026-03-14
**Theme:** Events Scraper — 3-tier architecture (structured + AI + deals)

### What Was Built

**DB migration** — `supabase/migrations/20260314000001_add_deal_fields.sql`
- Added `event_type`, `brand`, `discount_description`, `deal_category` to events table
- Indexes on `event_type` and `brand`

**Scraper infrastructure** (`services/events-scraper/scrapers/`)
- `models.py` — `RawEvent` dataclass, `EventType` + `DealCategory` enums
- `base.py` — `BaseScraper` with httpx retry, JSON-LD extraction, AI-ready HTML cleaning
- `publisher.py` — SQS batch publisher (10/batch), standard + FIFO queue support

**Config-driven source registry** (`config/sources.json`)
- 4 Tier 1 sources, 12 Tier 2 sources, 5 Tier 3 deal monitors
- Adding new Tier 2 source = 1 JSON entry, zero code

**Tier 1 scrapers** — 3-strategy cascade (LibCal API → JSON-LD → AI fallback)
- Fairfax County Library, Loudoun County Library, Arlington Library
- Eventbrite NoVa (5 city search URLs)

**Tier 2** — `AIEventExtractor` + `AITier2Scraper`
- Any URL → cleaned HTML → gpt-4o-mini → structured events
- Powers all 12 config-driven sources (dullesmoms, patch.com, etc.)

**Tier 3 deal monitors**
- `KrazyCouponLadyScraper` — restaurant/freebie deals from website
- `Hip2SaveScraper` — restaurant/family deals
- `GoogleNewsRssScraper` — Google News RSS + AI extraction for viral deals

**Lambda handler** — runs all 3 tiers, reports per-source stats

### Architecture Note
This is functionally an AI agent system: the Tier 2/3 scrapers autonomously
read, understand, and extract structured data from arbitrary web content.
The key difference from a full agent is bounded scope — each invocation has
a fixed URL list, not open-ended browsing.

---

## Session 2 — 2026-03-13 / 2026-03-14
**Theme:** Database — Supabase schema, migrations, pgvector

### What Was Built

**Local Supabase setup**
- Docker Desktop + Supabase CLI — local instance at http://127.0.0.1:54323
- Decision: local-first dev, migrate to paid cloud project at launch (ADR-008)
- Env files: `apps/web/.env.local`, `services/api/.env`

**Migrations (6 files in `supabase/migrations/`)**
- `000001` — pgvector + uuid-ossp in `extensions` schema
- `000002` — `locations` table, 15 NoVa locations seeded
- `000003` — `categories` table, 15 categories seeded
- `000004` — `events` table, 34 columns, RLS, 10 indexes, ivfflat vector index
- `000005` — `newsletter_subs` table, RLS
- `000006` — fixed newsletter INSERT policy (email regex, not `true`)

**Python utilities**
- `services/api/db.py` — cached Supabase client (shared by all Lambdas)
- `services/api/requirements.txt` — supabase, boto3
- `services/api/scripts/seed.py` — seeds test events, production guard

**TypeScript types**
- `apps/web/src/types/supabase.ts` — generated via `supabase gen types typescript --local`
- Note: PowerShell `>` outputs UTF-16; must use `| Out-File -Encoding UTF8`

### Notes
- Supabase CLI v2 uses `sb_publishable_*` / `sb_secret_*` key format (not JWT `eyJ...`)
- `supabase db push` requires a linked remote project; use `supabase migration up` for local
- `supabase db reset` resets local DB and replays all migrations cleanly
