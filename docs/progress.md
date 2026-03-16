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

## Session 9 — Terraform IaC ⬜
**Planned focus:** Full infrastructure as code

- ⬜ `infra/terraform/main.tf` (provider, backend)
- ⬜ `infra/terraform/s3.tf` (web, media, tfstate buckets)
- ⬜ `infra/terraform/cloudfront.tf` (2 distributions)
- ⬜ `infra/terraform/lambda.tf` (5 functions + IAM roles)
- ⬜ `infra/terraform/api_gateway.tf`
- ⬜ `infra/terraform/sqs.tf` (queues + DLQs)
- ⬜ `infra/terraform/eventbridge.tf`
- ⬜ `infra/terraform/ssm.tf` (parameter placeholders)
- ⬜ `infra/terraform/cloudwatch.tf` (dashboard + alarms)
- ⬜ `infra/terraform/variables.tf` + `outputs.tf`
- ⬜ `terraform init && terraform plan` clean

---

## Session 10 — CI/CD ⬜
**Planned focus:** 5 GitHub Actions workflows

- ⬜ `.github/workflows/test.yml` (pytest + type-check on PR)
- ⬜ `.github/workflows/deploy-frontend.yml` (build + S3 + CloudFront)
- ⬜ `.github/workflows/deploy-api.yml` (zip + Lambda update × 5)
- ⬜ `.github/workflows/lighthouse.yml` (Lighthouse CI on PR)
- ⬜ `.github/workflows/terraform.yml` (fmt + validate + plan, no auto-apply)
- ⬜ Secrets configured in GitHub repository settings
- ⬜ Branch protection rules on `main`

---

## Session 11 — SEO + Performance ⬜
**Planned focus:** Lighthouse 90+, sitemaps, structured data

- ⬜ `sitemap.xml` generation (Next.js metadata API)
- ⬜ `robots.txt`
- ⬜ JSON-LD on all event pages
- ⬜ JSON-LD LocalBusiness on home page
- ⬜ OG images for all event pages
- ⬜ Core Web Vitals: LCP <2.5s, CLS <0.1, TBT <300ms
- ⬜ Image optimization (WebP, explicit width/height)
- ⬜ Font preloading
- ⬜ Lighthouse CI passing all thresholds
- ⬜ Google Search Console verified

---

## Session 12 — Launch ⬜
**Planned focus:** Monitoring, alerting, go-live

- ⬜ CloudWatch dashboard `novakidlife-prod`
- ⬜ Alarms: Lambda error rate, DLQ depth, API 5xx rate
- ⬜ SNS alerts to email/SMS
- ⬜ Domain DNS configured (Route 53 → CloudFront)
- ⬜ SSL certificate (ACM)
- ⬜ `novakidlife.com` live and returning HTTP 200
- ⬜ First real events published
- ⬜ First social posts scheduled
- ⬜ Google Analytics / Plausible wired up
- ⬜ Go-live announcement
