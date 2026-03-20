# Build Progress — NovaKidLife (12 Sessions)

Legend: ✅ Complete | 🔄 In Progress | ⬜ Not Started

---

## Session 1 — Foundation ✅
**Date:** 2026-03-13

- ✅ Complete repo folder structure
- ✅ `CLAUDE.md` at repo root (full project bible)
- ✅ All 15 skill files in `/skills/`
  - ✅ `deploy-frontend.md`
  - ✅ `deploy-api.md`
  - ✅ `db-migrate.md`
  - ✅ `add-component.md`
  - ✅ `add-lambda.md`
  - ✅ `generate-event.md`
  - ✅ `generate-image.md`
  - ✅ `post-social.md`
  - ✅ `scrape-events.md`
  - ✅ `terraform-plan.md`
  - ✅ `terraform-apply.md`
  - ✅ `seed-db.md`
  - ✅ `test-api.md`
  - ✅ `check-lighthouse.md`
  - ✅ `monitor.md`
- ✅ Next.js 14 setup (`apps/web/`) with TypeScript + Tailwind
- ✅ Warm color system via CSS custom properties (amber primary, sage secondary)
- ✅ Self-hosted fonts configured: Nunito 600/700/800 + Plus Jakarta Sans 400/500/600
- ✅ Base `package.json` for `apps/web/` and all 5 services
- ✅ `docs/` directory with all documentation files
- ✅ Run `node apps/web/scripts/download-fonts.mjs`
- ✅ `cd apps/web && npm install` (npm resolved to Next.js 15.5.12)
- ✅ Verify `npm run dev` renders correctly — color swatches + type specimen confirmed at localhost:3000

---

## Session 2 — Database ✅
**Date:** 2026-03-13 / 2026-03-14
**Planned focus:** Supabase schema, migrations, pgvector

- ✅ Supabase running locally via Docker (supabase CLI + Docker Desktop)
- ✅ `events` table migration (34 columns including `embedding extensions.vector(1536)`)
- ✅ `categories` table migration (15 categories seeded)
- ✅ `locations` table migration (15 NoVa locations seeded)
- ✅ `newsletter_subs` table migration
- ✅ Row Level Security policies on all tables
- ✅ pgvector extension enabled (in `extensions` schema)
- ✅ Indexes: `start_at`, `status`, `source_url` (unique), geo, tags (GIN), ivfflat embedding
- ✅ `update_updated_at()` trigger with `security definer` + fixed `search_path`
- ✅ Supabase types exported to `apps/web/src/types/supabase.ts` (UTF-8)
- ✅ Python Supabase client utility: `services/api/db.py`
- ✅ Seed script: `services/api/scripts/seed.py`
- ✅ ADR-008 logged: Local Supabase via Docker (free tier limit workaround)

---

## Session 3 — Events Scraper ✅
**Date:** 2026-03-14
**Planned focus:** Lambda + SQS pipeline — expanded to full 3-tier scraper architecture

- ✅ DB migration: `event_type`, `brand`, `discount_description`, `deal_category` added to events
- ✅ `scrapers/models.py` — `RawEvent`, `EventType`, `DealCategory`
- ✅ `scrapers/base.py` — `BaseScraper` with httpx, retry, JSON-LD extraction, HTML cleaning
- ✅ `scrapers/publisher.py` — SQS batch publisher (10/batch)
- ✅ `config/sources.json` — config-driven registry (4 Tier1, 12 Tier2, 5 Tier3 sources)
- ✅ Tier 1: Fairfax, Loudoun, Arlington library scrapers (LibCal API + JSON-LD + AI fallback)
- ✅ Tier 1: Eventbrite NoVa scraper (JSON-LD across 5 city URLs)
- ✅ Tier 2: `AIEventExtractor` + `AITier2Scraper` (gpt-4o-mini, config-driven, no code per source)
- ✅ Tier 3: `KrazyCouponLadyScraper`, `Hip2SaveScraper` (AI HTML extraction)
- ✅ Tier 3: `GoogleNewsRssScraper` (free RSS, AI deal extraction, viral deal detection)
- ✅ `handler.py` — Lambda entry point, runs all 3 tiers, reports stats
- ✅ `requirements.txt` + `requirements-dev.txt`
- ✅ Unit tests for `RawEvent` model
- ⬜ Lambda deployed to AWS (Session 9 — Terraform)
- ⬜ EventBridge rule created (Session 9)
- ⬜ `birthday_freebies.py` scraper (Session 4 stretch)

---

## Session 4 — Image Generation ✅
**Date:** 2026-03-14
**Planned focus:** Imagen 3 / DALL-E 3 Lambda — two pipeline design (website photo + social illustration)

- ✅ DB migration: 8 image SEO columns added (`image_alt`, `image_width`, `image_height`, `image_blurhash`, `image_url_md`, `image_url_sm`, `social_image_url`, `og_image_url`)
- ✅ `prompts.py` — full prompt library (14 event types × 2 styles: photorealistic + flat illustration)
- ✅ `sourcer.py` — image sourcing cascade (scraped URL → Google Places Photos → None)
- ✅ `generator.py` — Imagen 3 primary, DALL-E 3 fallback, provider-agnostic bytes output
- ✅ `enhancer.py` — warm color grade (warmth shift, contrast, saturation, vignette)
- ✅ `processor.py` — all variants: hero 1200×675, hero-md 800×450, hero-sm 400×225, card 600×400, og 1200×630, social 1080×1080, LQIP base64, blurhash
- ✅ `alt_text.py` — AI alt text via gpt-4o-mini (≤125 chars, SEO + a11y)
- ✅ `uploader.py` — S3 upload with 1-year cache headers, CDN URL generation, skip-if-exists
- ✅ `handler.py` — Lambda SQS trigger, full pipeline orchestration, Supabase PATCH
- ✅ `requirements.txt` — boto3, Pillow, httpx, openai, google-cloud-aiplatform, blurhash-python, supabase
- ✅ `tests/test_processor.py` — 14 tests covering all size variants, WebP format, LQIP, size limits
- ✅ Full source expansion (between Session 5 and Session 6):
  - `scrapers/tier1/meetup.py` — Meetup API OAuth scraper (family groups + Pokémon TCG meetups, 30mi radius)
  - `config/sources.json` expanded: 5 Tier 1 → Meetup added; 12 → 46 Tier 2 sources total
    - 11 new Patch cities (Vienna, McLean, Herndon, Springfield, Burke, Centreville, Manassas, Falls Church, Alexandria, Woodbridge, Sterling)
    - 7 local news sites (Reston Now, ARLnow, FFXnow, Loudoun Now, InsideNova, Washingtonian Kids, DCist)
    - 6 government/parks sources (Prince William, Alexandria City, Falls Church, NOVA Parks, Reston Community Center, YMCA)
    - 10 venues (Wolf Trap, Meadowlark, Frying Pan Farm, Cox Farms, Burnside Farms, Great Country Farms, Wegmeyer Farms, Udvar-Hazy, GMU Arts, The ARC)
  - `services/events-scraper/.env` created with MEETUP_CLIENT_ID / MEETUP_CLIENT_SECRET placeholders
  - `docs/env-variables.md` updated with Meetup SSM paths
  - Facebook Events + Nextdoor AI agent approach deferred — saved to memory for future session
- ✅ Pokémon TCG section added (between Session 4 and Session 5):
  - Migration `20260314000003_add_section_field.sql` — `section` column (default 'main')
  - `scrapers/pokemon/events_scraper.py` — Play! Pokémon locator + 5 NoVa LGS
  - `scrapers/pokemon/drops_scraper.py` — release calendar + 15-store NoVa retailer matrix
  - `models.py` updated — `POKEMON_TCG` + `PRODUCT_DROP` event types, `section` + `slug` fields
  - `config/sources.json` updated — `pokemon_events` section with 3 sources + Google News queries
  - `handler.py` (scraper) updated — runs Pokemon scrapers in new dedicated tier
  - `prompts.py` (image-gen) updated — 7 Pokémon-specific prompts (league/prerelease/regional/drops)
  - `handler.py` (image-gen) updated — routes pokemon section to Pokémon prompts
- ⬜ Lambda deployed to AWS (Session 9 — Terraform)
- ⬜ SQS queue + DLQ wired (Session 9)

---

## Session 5 — API ✅
**Date:** 2026-03-14
**Planned focus:** API Gateway + Lambda REST endpoints

- ✅ `services/api/handler.py` — Lambda entry point, 15 routes registered
- ✅ `services/api/router.py` — lightweight Lambda proxy router (path params, CORS, 500 catch)
- ✅ `services/api/models.py` — Pydantic: SearchRequest, NewsletterSubscribeRequest, helpers
- ✅ `services/api/routes/events.py` — GET /events (7 filters), /events/featured, /events/upcoming, /events/{slug}, POST /events/search (pgvector)
- ✅ `services/api/routes/pokemon.py` — GET /pokemon/events, /pokemon/drops, /pokemon/retailers
- ✅ `services/api/routes/categories.py` — GET /categories (with event counts)
- ✅ `services/api/routes/locations.py` — GET /locations (with event counts)
- ✅ `services/api/routes/newsletter.py` — POST /newsletter/subscribe (upsert, email validation)
- ✅ `services/api/routes/sitemap.py` — GET /sitemap (slugs split by section for Next.js build)
- ✅ `services/api/routes/admin.py` — POST /admin/events/trigger-scrape, GET /admin/health/detailed (X-Api-Key protected)
- ✅ `supabase/migrations/20260314000004_add_search_rpc.sql` — pgvector search_events() RPC function
- ✅ `services/api/requirements.txt` — updated (pydantic, openai added)
- ✅ `services/api/tests/test_router.py` — 20 tests (router, models, CORS, 404, 500)
- ⬜ API Gateway configured (Session 9 — Terraform)
- ⬜ Custom domain api.novakidlife.com (Session 9)

---

## Session 6 — Frontend: Events Listing ✅
**Date:** 2026-03-14
**Planned focus:** Events browse page with filtering

- ✅ `src/types/events.ts` — Event, Category, Location, EventsResponse, EventsParams TypeScript types
- ✅ `src/lib/api.ts` — full API client (getEvents, getEvent, search, categories, locations, pokemon, featured, upcoming)
- ✅ `src/components/BlurImage.tsx` — LQIP blur-up with CSS fade transition, explicit dimensions for CLS prevention
- ✅ `src/components/EventCard.tsx` — article card (blur image, date/time, title 2-line clamp, location pin, cost badge, tags)
- ✅ `src/components/EventCardSkeleton.tsx` — pulse skeleton + EventGridSkeleton (count prop)
- ✅ `src/components/EventGrid.tsx` — responsive 1→2→3 column grid, priority LCP on first 3 cards
- ✅ `src/components/SearchBar.tsx` — 500ms debounce, loading spinner, clear button, accessible
- ✅ `src/components/FilterBar.tsx` — date presets (Today/Weekend/Week/Month), category dropdown, Free toggle, Clear all, result count
- ✅ `src/components/Pagination.tsx` — numbered with ellipsis, prev/next, aria-current
- ✅ `src/components/EmptyState.tsx` — friendly copy, clear filters CTA
- ✅ `src/app/events/EventsClient.tsx` — 'use client', URL-synced state (q/date/category/free/page), semantic search path + filter path, Suspense-safe
- ✅ `src/app/events/page.tsx` — server component, full metadata + OG, Suspense boundary

---

## Session 7 — Frontend: Event Detail ✅
**Date:** 2026-03-14
**Planned focus:** Individual event page with full SEO+GEO

- ✅ `src/app/events/[slug]/page.tsx` — `generateStaticParams` (from `/sitemap` API) + `generateMetadata` (SEO title/description to spec)
- ✅ Hero image with blur placeholder (LQIP, priority=true for LCP)
- ✅ Event metadata section (date, time, location, age range, cost) with icon cards
- ✅ Full event description + tag chips
- ✅ `src/components/ShareButtons.tsx` — copy link, Twitter/X, Facebook
- ✅ `src/components/RelatedEvents.tsx` — 3 related events by section + tags (client fetch)
- ✅ `src/components/EventJsonLd.tsx` — Event + BreadcrumbList + FAQPage schemas
- ✅ `src/components/Breadcrumbs.tsx` — visual breadcrumb nav with chevron separators
- ✅ Back-to-list navigation link
- ✅ Visible FAQ section (GEO: Q&As for AI systems + Google featured snippets)
- ✅ How to Register section (only when registration_url exists)
- ✅ Google Maps link (when lat/lng available)
- ✅ `src/app/sitemap.ts` — dynamic sitemap.xml (static pages + all event slugs with lastmod)
- ✅ `src/app/robots.ts` — robots.txt allowing all crawlers + explicit AI bot list
- ✅ `public/llms.txt` — GEO file for LLM crawlers (site description, sections, data sources)
- ✅ `src/app/page.tsx` — WebSite schema (sitelinks searchbox) + LocalBusiness schema (4 NoVa counties)
- ✅ `src/app/events/page.tsx` — meta description trimmed from 169→143 chars (within 155 limit)

---

## Session 8 — Social Poster ✅
**Date:** 2026-03-15
**Planned focus:** Buffer API integration

- ✅ `supabase/migrations/20260315000001_add_social_tracking.sql` — `social_posted_platforms text[]` + `social_posted_at timestamptz` columns + GIN index
- ✅ `services/social-poster/ssm.py` — SSM parameter helper with local `.env` fallback
- ✅ `services/social-poster/buffer_client.py` — `Platform` enum (TWITTER/INSTAGRAM/FACEBOOK), `BufferClient`, `BufferProfile`, `BufferUpdate` dataclasses
- ✅ `services/social-poster/scheduler.py` — `next_optimal_slot()` (Eastern timezone, weekday 9/12/5pm, weekend 10am/2pm, quiet hours 10pm–7am), `slots_for_week()`, `is_quiet_hours()`
- ✅ `services/social-poster/copy_builder.py` — `build_copy(event, platform)` dispatches to:
  - `_build_twitter()` — 280 char limit (t.co = 23 chars), 2–3 hashtags, event type emoji prefix
  - `_build_instagram()` — 10–15 hashtag block, "Link in bio" CTA, date/time emoji cards
  - `_build_facebook()` — medium length, full address, 1–2 hashtags
  - Full hashtag library: core, local (city), events, free, Pokémon, seasonal
- ✅ `image_url_for_platform()` — Instagram gets `social_image_url` (1080×1080), Twitter/Facebook get `og_image_url` (1200×630)
- ✅ `services/social-poster/handler.py` — EventBridge-triggered Lambda (schedule, not SQS), queries DB for unposted events, posts to all 3 platforms, marks `social_posted_platforms`, MAX_EVENTS_PER_RUN = 5, dry_run support
- ✅ `services/social-poster/requirements.txt` + `requirements-dev.txt`
- ✅ `services/social-poster/.env` — Buffer token, profile IDs, Supabase config
- ✅ `services/social-poster/tests/test_copy_builder.py` — 20+ tests (char limits, URLs, hashtags, platform routing, Pokémon, deal copy, image URL selection)
- ✅ `services/social-poster/tests/test_scheduler.py` — 15+ tests (future datetime, timezone-aware, quiet hours, valid slot hours, weekday/weekend routing, consecutive slots)
- ✅ `skills/social-strategy.md` — Twitter algorithm optimization, hashtag playbook, content calendar
- ✅ `skills/brand-voice.md` — voice attributes, tone by context, language rules, user personas
- ✅ `skills/content-generation.md` — copy templates for all event types + platforms
- ✅ `skills/autonomous-agents.md` — architecture diagram, event lifecycle, CloudWatch alarms
- ✅ `skills/mcp-builder.md` — 3 planned MCPs, FastMCP patterns, design principles
- ✅ `skills/skill-creator.md` — skill format spec, quality checklist, 6-step creation process
- ⬜ Run `supabase migration up` to apply social tracking migration
- ⬜ Lambda deployed to AWS (Session 9 — Terraform)
- ⬜ EventBridge schedule rule (Session 9)
- ⬜ Buffer profile IDs in SSM Parameter Store (at launch)

---

## Session 9 — Terraform IaC ✅
**Date:** 2026-03-15 (included in initial commit `728916b`)

- ✅ `infra/terraform/main.tf` — AWS provider, S3 backend (`novakidlife-tfstate`), DynamoDB lock (`novakidlife-tflock`)
- ✅ `infra/terraform/s3.tf` — web, media, tfstate buckets; OAC for CloudFront
- ✅ `infra/terraform/cloudfront.tf` — 2 distributions (web + media CDN); CloudFront Function for trailing-slash rewrite
- ✅ `infra/terraform/lambda.tf` — 5 Lambda functions (api, events-scraper, image-gen, social-poster, scheduler) + IAM roles + policies
- ✅ `infra/terraform/api_gateway.tf` — HTTP API Gateway + Lambda integration + custom domain `api.novakidlife.com`
- ✅ `infra/terraform/sqs.tf` — events queue + DLQ; Lambda event source mapping
- ✅ `infra/terraform/eventbridge.tf` — scraper schedule rule (daily 6am EST)
- ✅ `infra/terraform/ssm.tf` — SSM parameter placeholder registry for all secrets
- ✅ `infra/terraform/cloudwatch.tf` — CloudWatch dashboard + Lambda error/duration alarms + SQS DLQ alarm
- ✅ `infra/terraform/variables.tf` + `outputs.tf` — all variables + resource ARN outputs
- ✅ `terraform init && terraform plan` clean

---

## Session 10 — CI/CD ✅
**Date:** 2026-03-15 (included in initial commit `728916b`)

- ✅ `.github/workflows/test.yml` — pytest (all services) + Next.js type-check on PR
- ✅ `.github/workflows/deploy-frontend.yml` — build + S3 sync + CloudFront invalidation on push to main
- ✅ `.github/workflows/deploy-api.yml` — zip + Lambda update for api, events-scraper, image-gen, content-generator
- ✅ `.github/workflows/lighthouse.yml` — Lighthouse CI on PR (performance/accessibility/SEO thresholds)
- ✅ `.github/workflows/terraform.yml` — fmt + validate + plan on PR (no auto-apply)
- ✅ GitHub Actions secrets configured (AWS credentials, Supabase keys, etc.)
- ✅ Lambda function names fixed to `novakidlife-prod-*` pattern (commit `3241cb1`)

---

## Session 11 — SEO + Performance ✅
**Date:** 2026-03-16

### Skills & Infrastructure ✅
- ✅ `skills/seo-geo.md` massively expanded — Fortune 100 level (13 sections: tech SEO, JSON-LD, keyword strategy, E-E-A-T, content architecture, GEO, Core Web Vitals, sitemap, robots, analytics, competitive positioning, pre-ship checklist)
- ✅ `skills/local-seo.md` created — bulletproof local SEO playbook (GBP setup, 4-tier citations, local link building with outreach templates, hyperlocal targeting, Pokémon TCG local SEO, 12-month timeline)
- ✅ `skills/qa-build.md` created — pre-build checklist + all Next.js 15 static export gotchas documented
- ✅ Buffer API → Ayrshare swap (`services/social-poster/buffer_client.py` → `AyrshareClient`, `handler.py` + `ssm.py` updated)
- ✅ `.gitattributes` created — LF line endings for all text files (resolves Windows CRLF warnings)
- ✅ Initial git commit of all 8 sessions' work + pushed to GitHub

### Frontend — New Pages ✅
- ✅ `src/app/about/page.tsx` — E-E-A-T about page
- ✅ `src/app/privacy-policy/page.tsx` — privacy policy (noindex)
- ✅ `src/app/pokemon/page.tsx` — full Pokémon TCG hub with JSON-LD
- ✅ `src/app/layout.tsx` — updated with root metadata, font variables, Header + Footer wrappers

### Frontend — New Components ✅
- ✅ `src/components/Header.tsx` — sticky nav (logo, links, CTA)
- ✅ `src/components/Footer.tsx` — dark sage footer with social icons

### Homepage V2 — Shell ✅
- ✅ `src/app/page.tsx` rewritten — V2 layout structure with JSON-LD schemas; component imports added in Session 13

---

## Session 8b — Content Generator + Blog ✅
**Date:** 2026-03-18 (commit `22043e7`)

- ✅ `services/content-generator/handler.py` — Lambda entry point; EventBridge triggers Thu 8pm + Mon 6am EST; SSM bootstrap
- ✅ `services/content-generator/post_builder.py` — 5 prompt builders (weekend, location, free_events, week_ahead, indoor); idempotency via `post_exists()` check
- ✅ `services/content-generator/prompts.py` — 328-line prompt library; shared voice rules + FAQ instructions injected into every prompt
- ✅ `services/content-generator/github_trigger.py` — triggers `deploy-frontend` workflow via GitHub repository dispatch API after new posts saved
- ✅ `services/content-generator/ssm.py` — SSM helper (SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY, GITHUB_TOKEN)
- ✅ `services/content-generator/tests/test_post_builder.py` — 205 lines, 20+ tests
- ✅ `supabase/migrations/20260318000001_create_blog_posts.sql` — blog_posts table with RLS, GIN index on event_ids[], idempotency unique constraint
- ✅ `services/api/routes/blog.py` — `GET /blog` (paginated, filtered) + `GET /blog/{slug}` (with joined event previews)
- ✅ `apps/web/src/app/blog/page.tsx` — blog listing; server component; metadata; Suspense skeleton
- ✅ `apps/web/src/app/blog/[slug]/page.tsx` — blog detail; Article + BreadcrumbList + Event JSON-LD; Markdown renderer; EventCard grid; social share buttons
- ✅ `apps/web/src/types/blog.ts` — BlogPost, PostCard, BlogListResponse TypeScript types
- ✅ `apps/web/src/lib/api.ts` — added `getBlogPosts()` + `getBlogPost()` client functions
- ✅ `skills/brand-voice.md` — blog voice section added (328 lines): parent-to-parent tone, logistics blocks 📅📍💰, GEO/FAQ optimization, AI generation prompt reference
- ✅ `docs/competitor-analysis.md` — 389-line competitive analysis (Mommy Poppins, Macaroni Kid, DC Metro Moms, Eventbrite, Patch)
- ✅ `infra/terraform/lambda.tf` — content-generator Lambda + IAM role/policy
- ✅ `infra/terraform/eventbridge.tf` — 2 new EventBridge rules for content-generator (Thu + Mon schedules)
- ✅ `services/events-scraper/config/sources.json` — expanded 59 → 111 Tier 2 sources (+52: Macaroni Kid, Mommy Poppins, Patch cities, NPS parks, town pages, shopping centers)

---

## Session 12 — Launch ✅
**Date:** 2026-03-18

### Terraform IaC Fixes
- ✅ `social_poster` Lambda removed from Terraform (code preserved in `services/social-poster/`; removed from `lambda.tf`, `cloudwatch.tf`, `outputs.tf`)
- ✅ `cloudfront.tf` — removed `logging_config` (conflicts with bucket ownership controls / ACL disabled on modern S3)
- ✅ `cloudwatch.tf` — added `region` to all dashboard widget properties (required by CloudWatch API); reformatted for `terraform fmt` compliance
- ✅ `ssm.tf` — replaced `buffer/*` params with `ayrshare/api-key`; added `unsplash/access-key` + `pexels/api-key`
- ✅ `terraform apply` — all resources provisioned in AWS

### Infrastructure Live
- ✅ ACM wildcard cert (`*.novakidlife.com`) issued in us-east-1
- ✅ Route 53 DNS — `novakidlife.com` + `www` → CloudFront; `api.novakidlife.com` → API Gateway
- ✅ `media.novakidlife.com` → media CloudFront distribution
- ✅ `novakidlife.com` returning HTTP 200 — site is LIVE

### Lambda Deploy Script
- ✅ `scripts/deploy-lambdas.py` — Python build + deploy script; pip installs manylinux-compatible dependencies; zips; uploads via S3 for packages >50MB; updates Lambda function code

### Supabase Cloud
- ✅ Cloud project linked (`ovdnkgpdgkceulkpwedj` — `supabase link --project-ref ovdnkgpdgkceulkpwedj`)
- ✅ All 12 migrations pushed to cloud (`supabase db push`)
- ✅ SSM secrets populated in Parameter Store for all Lambda functions

### Event Pipeline End-to-End Fix
- ✅ `image-gen/handler.py` — added `_upsert_event()` Step 0: upserts RawEvent → Supabase before image generation; maps RawEvent fields to DB column names (`full_description`, `venue_name`, `address`)
- ✅ `api/routes/events.py` + `routes/pokemon.py` — fixed SELECT column names to match DB schema (`full_description`, `venue_name`, `address` instead of aliases)
- ✅ `api/handler.py` — added blog route registration, SSM bootstrap, `handler` alias
- ✅ `events-scraper/handler.py` — added SSM bootstrap
- ✅ `api/requirements.txt` — added `pydantic[email]` + `email-validator`

### Image Sourcing — 5-Step Cascade
- ✅ `image-gen/sourcer.py` — Unsplash API (Step 3) + Pexels API (Step 4) added before AI generation fallback
- ✅ `_build_search_query()` — maps event_type / category / tags to stock photo search terms
- ✅ Deals + product drops skip free stock (AI-generated branded imagery performs better)

### Homepage V2 Components
- ✅ `src/app/not-found.tsx` — custom 404 (required for App Router static export)
- ✅ `src/app/error.tsx` — error boundary (`'use client'`)
- ✅ `src/app/global-error.tsx` — global error boundary (`'use client'`)
- ✅ `src/components/HeroSearch.tsx` — Airbnb-style search + weekly calendar strip + social proof
- ✅ `src/components/WeekendEventsSection.tsx` — Sat/Sun tab toggle + ❤️ save + ⭐ Editor's Pick
- ✅ `src/components/FreeEventsSection.tsx` — free events spotlight
- ✅ `src/components/CityStripsSection.tsx` — 4 city event strips
- ✅ `src/components/NewsletterForm.tsx` — 4-state machine, POSTs to API
- ✅ `src/app/page.tsx` — imports all components wired into 10-section layout

### Next.js / Web Fixes
- ✅ `next.config.js` — removed `async headers()` (not supported with `output: 'export'`)
- ✅ `robots.ts` + `sitemap.ts` — added `export const dynamic = 'force-static'`
- ✅ `events/[slug]/page.tsx` — `params` typed as `Promise<{slug}>`, awaited; `dynamicParams = false`; `notFound()` outside try/catch; `_placeholder` fallback in `generateStaticParams`

---

## Session 14 — 2026-03-19 ✅

### API Domain — api.novakidlife.com Live
- ✅ `terraform.tfvars` — added `api_acm_certificate_arn` (reused existing `*.novakidlife.com` wildcard cert)
- ✅ `terraform apply` — created `aws_api_gateway_domain_name.api[0]` + `aws_api_gateway_base_path_mapping.api[0]`
- ✅ Route 53 CNAME record: `api.novakidlife.com` → `d-jamvbuw68d.execute-api.us-east-1.amazonaws.com`
- ✅ `curl https://api.novakidlife.com/events` returning HTTP 200

### Lambda Dependency Deploys
- ✅ `scripts/deploy-lambdas.py` — added `content-generator` to SERVICES dict
- ✅ All 4 Lambdas redeployed with manylinux pip dependencies: `api`, `events-scraper`, `image-gen`, `content-generator`
- ✅ `blog_posts` migration pushed to cloud Supabase (`supabase db push`)

### SSM Secrets
- ✅ `/novakidlife/github/token` — GitHub fine-grained PAT added (Actions: read+write on novakidlife repo)

### Seasonal Content Generator
- ✅ `services/content-generator/prompts.py` — `build_seasonal_prompt()` added: seasonal hook, insider angle rules, time-sensitive notes, seasonal FAQ targeting
- ✅ `services/content-generator/post_builder.py`:
  - `get_seasonal_context()` — auto-detects seasonal theme from date: Easter (21 days out), Cherry Blossom (Mar 10–Apr 15), Spring Break (Mar 21–Apr 7), Mother's Day, Memorial Day, Halloween, Holiday Season
  - `PostSpec` — added `season_name`, `focus_keywords`, `seo_title` optional fields
  - `_build_specs()` — appends `seasonal` spec to weekend trigger when `get_seasonal_context()` returns a theme
  - `_select_prompt()` + `_make_slug()` — wired for `seasonal` post type
- ✅ Content generator redeployed — first Thursday run will generate Easter + Cherry Blossom posts

### First Scraper Run
- ✅ `events-scraper` triggered manually — running against 111 sources (in progress)
- ✅ Scraper sources updated (new sources committed)

### Pending (carried to Session 15)
- ⬜ Confirm scraper results — check event count in DB
- ⬜ Verify image pipeline processed events (photos on event cards)
- ⬜ Wire homepage sections to live API (currently placeholder data)
- ⬜ Manually trigger content generator after events populate
- ⬜ Google Search Console verified
- ⬜ Lighthouse CI passing all thresholds
- ⬜ First social posts via Ayrshare

---

## Session 15 — 2026-03-19 ✅
**Planned focus:** CORS fix, homepage API wiring

### CORS Fix ✅
- ✅ `services/api/router.py` — dynamic `_cors_headers(origin)` reflects request origin if in `_ALLOWED_ORIGINS`
- ✅ `services/api/routes/events.py` — all 5 handlers propagate `event["_origin"]` to `ok()` / `error()`
- ✅ `services/api/routes/pokemon.py` — all 3 handlers updated
- ✅ API Lambda redeployed

### Image Pipeline Fixes ✅
- ✅ `image-gen/handler.py` — `_make_slug()`: slug generated from title + md5(source_url); random seed when source_url empty
- ✅ `image-gen/handler.py` — removed non-existent `image_lqip` column from PATCH payload
- ✅ `image-gen/handler.py` — added `resp.text` logging on upsert failures
- ✅ image-gen Lambda redeployed; test invocation confirmed `ok: 1, errors: 0`
- ✅ DLQ redriven twice; scraper retriggered

### Homepage Wiring ✅
- ✅ `page.tsx` — blog section fetches `/blog?limit=3` as async server component; falls back to placeholders
- ✅ `HeroSearch.tsx` — `DAY_COUNTS` replaced with live `useEffect` fetch; real counts per day
- ✅ Homepage sections (`WeekendEventsSection`, `FreeEventsSection`, `CityStripsSection`) confirmed already API-wired

### Scraper Source Fixes ✅
- ✅ `sources.json` — `birthday-freebies` disabled (`birthday_freebies.py` was never built)
- ✅ `krazy_coupon_lady.py` — 3 dead URLs updated to current site structure

### Frontend Build + Deploy ✅
- ✅ `npm run build` (two passes) — clean export
- ✅ `aws s3 sync` → `novakidlife-web`
- ✅ CloudFront `/*` invalidation — `https://novakidlife.com` returning HTTP 200

### Pending (carried forward)
- ⬜ Confirm images on event cards (image-gen processing in background)
- ⬜ Trigger content generator (once events + images confirmed)
- ⬜ Google Search Console — submit sitemap, verify ownership
- ⬜ First social posts via Ayrshare (pending Ayrshare account setup)

---

## Session 16 — 2026-03-20 ✅
**Theme:** Homepage fix, stale data cleanup, daily auto-deploy, docs refresh

### Critical Bug Fix — Wrong API URL in Build ✅
- ✅ `apps/web/.env.local` — `NEXT_PUBLIC_API_URL` changed from `http://localhost:3001` → `https://api.novakidlife.com`
- ✅ `NEXT_PUBLIC_SITE_URL` changed from `http://localhost:3000` → `https://novakidlife.com`
- Root cause: production build was baking localhost URL into static bundle; all client-side fetches silently failed

### Stale Data Cleanup ✅
- ✅ Deleted 21 events with `start_at < 2026-03-20` via Supabase REST API (old 2021–2023 deal dates)
- ✅ 53 current + future events remain in DB

### Frontend Rebuild + Deploy ✅
- ✅ `npm run build` — clean, single-pass, all 13 pages exported
- ✅ `aws s3 sync out/ s3://novakidlife-web --delete` — full deploy
- ✅ CloudFront invalidation `E1GSDDQH95EO6C` `/*` — ID: `I2L3MM1FNE76GIZZ7739L5HWB6`

### Daily Auto-Deploy ✅
- ✅ `.github/workflows/deploy-frontend.yml` — added `schedule: cron: '0 15 * * *'` (10am EST daily)
- ✅ Pushed to main → GitHub Actions now rebuilds site automatically every morning

### Scraper Re-triggered ✅
- ✅ `novakidlife-prod-events-scraper` Lambda triggered (202 accepted) — fresh events incoming

### Documentation Refresh ✅
- ✅ `docs/system-map.md` — full update: sessions 1-15, all new components, content-generator Lambda, 111 sources, Ayrshare SSM params
- ✅ `docs/env-variables.md` — Buffer→Ayrshare, added image sourcing vars, added content-generator section, SSM index updated
- ✅ `docs/errors-and-fixes.md` — 7 new entries from sessions 12-15
- ✅ `docs/social-media-log.md` — Buffer→Ayrshare throughout, setup checklist added

### Pending
- ⬜ Set GitHub secret `NEXT_PUBLIC_API_URL=https://api.novakidlife.com` in repo settings (for GitHub Actions builds)
- ⬜ Confirm images processing on event cards (image-gen pipeline running)
- ⬜ Trigger content generator (once events confirmed in DB with images)
- ⬜ Google Search Console — submit sitemap.xml, verify ownership
- ⬜ Ayrshare account setup + social-poster Lambda deployment
- ⬜ Monitor daily scraper + 10am rebuild for first full autonomous cycle
