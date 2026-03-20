# Dev Log — NovaKidLife

---

## Session 15 — 2026-03-19
**Theme:** CORS origin fix, route handler propagation, homepage API wiring

### CORS — Dynamic Origin Reflection
The router was hardcoding `Access-Control-Allow-Origin: https://www.novakidlife.com`, which blocked requests from `https://novakidlife.com` (non-www). Browser CORS errors were appearing on the homepage because CloudFront serves the non-www origin.

**Fix (`services/api/router.py`):**
- Added `_ALLOWED_ORIGINS` set: `novakidlife.com` + `www.novakidlife.com`
- `_cors_headers(origin)` — reflects back the request origin if it's in the allowed set, else defaults to `https://novakidlife.com`
- `dispatch()` — extracts `origin` header (case-insensitive), stashes in `event["_origin"]`
- All `ok()` / `error()` calls in dispatch now pass `origin` through

**Fix (route handlers):**
- `services/api/routes/events.py` — all 5 handlers (`list_events`, `featured_events`, `upcoming_events`, `get_event`, `search_events`) extract `event.get("_origin")` and pass it to every `ok()` / `error()` call
- `services/api/routes/pokemon.py` — all 3 handlers (`pokemon_events`, `pokemon_drops`, `pokemon_retailers`) updated same way

### Image Pipeline Debugging + Fixes

Three bugs found and fixed in `services/image-gen/handler.py`:

**Bug 1 — Upsert 400: missing slug**
`slug` is `NOT NULL UNIQUE` with no DB default. Upsert was sending no slug → 400 on every event. Fix: added `_make_slug(title, source_url)` — generates `{title-slug}-{md5hex[:6]}` from source URL. When source_url is empty, uses `secrets.token_hex(8)` as seed to prevent duplicate slugs.

**Bug 2 — PATCH 400: non-existent column**
`db_payload` included `"image_lqip": processed.lqip_data_url` but the DB schema has no `image_lqip` column (only `image_blurhash`). Removed from payload.

**Bug 3 — Silent failures swallowing errors**
`process_event()` catches all exceptions and returns `{"status": "error"}`. Lambda returns HTTP 200 → SQS considers message "processed" and deletes it. Events that failed never went to DLQ a second time. Added `resp.text` logging before `raise_for_status()` to expose Supabase error bodies in future.

**Fix sequence:** Deploy → DLQ redrive → confirmed `ok: 1, errors: 0` on test invocation → retrigger scraper.

### Homepage Wiring
All three homepage sections (`WeekendEventsSection`, `FreeEventsSection`, `CityStripsSection`) were already fetching from the live API — they just showed empty states because the DB was empty. No code changes needed.

Two remaining hardcoded items were wired:
- `page.tsx` — blog section now fetches `/blog?limit=3` as async server component at build time; falls back to placeholder cards when no posts exist; "All guides →" link updated to `/blog`
- `HeroSearch.tsx` — `DAY_COUNTS` replaced with `useEffect` fetch of current week's events; counts per day shown live in calendar strip (blank when 0)

### Scraper Source Fixes
- `sources.json` — `birthday-freebies` set `enabled: false` (`scrapers/tier3/birthday_freebies.py` was never built)
- `krazy_coupon_lady.py` — 3 dead URLs updated to current KrazyCouponLady site structure

### Frontend Build + Deploy
- `npm run build` (two passes) — clean, no errors
- `aws s3 sync` — pushed to `novakidlife-web` bucket
- CloudFront invalidation `E1GSDDQH95EO6C` — `/*` invalidated
- `https://novakidlife.com` returning HTTP 200 with updated `last-modified`

---

## Session 14 — 2026-03-19
**Theme:** API domain live, Lambda deploys, seasonal content generator, first scraper run

### api.novakidlife.com
The custom domain was never created — `api_acm_certificate_arn` was missing from `terraform.tfvars`. Fixed by reusing the existing `*.novakidlife.com` wildcard cert (already in us-east-1, valid for regional API Gateway). Added cert ARN to tfvars, ran `terraform apply` (created `aws_api_gateway_domain_name` + base path mapping), added Route 53 CNAME record manually. API now responding at `https://api.novakidlife.com`.

### Lambda Dependency Deploys
All four Lambdas were deployed via Terraform with source-only zips (no pip dependencies). The `deploy-lambdas.py` script was only missing `content-generator` — added it to the SERVICES dict. Ran the script for all four: api, events-scraper, image-gen, content-generator. Each package installs manylinux-compatible wheels for Python 3.12 Lambda runtime. Also pushed `blog_posts` migration to cloud Supabase (`supabase db push`) and added `/novakidlife/github/token` to SSM (GitHub fine-grained PAT with Actions read+write).

### Seasonal Content Generator
Added a `seasonal` post type that auto-detects the current holiday/season and generates a targeted SEO post. The detection logic (`get_seasonal_context()`) returns a season name, focus keywords, and pre-built SEO title based on the current date:

| Window | Season |
|--------|--------|
| 21 days before Easter | Easter egg hunts + spring activities |
| Mar 10 – Apr 15 | Cherry blossom season |
| Mar 21 – Apr 7 | Spring break |
| 14 days before Mother's Day | Mother's Day |
| 7 days before Memorial Day | Memorial Day weekend |
| October | Halloween + fall activities |
| Dec 1–24 | Holiday season |

Easter takes priority over cherry blossom (both active now — Easter is April 5, cherry blossom peak is March 22). The seasonal post fires as part of the Thursday weekend trigger alongside the existing 6 post types. `build_seasonal_prompt()` emphasizes insider local knowledge, time-sensitive notes (peak bloom window, sell-out risk), and FAQ questions targeting exact parent search queries.

### First Scraper Run
Triggered `novakidlife-prod-events-scraper` manually. Running against 111 sources — expected to take 10–15 minutes. 404s and 403s on some sources are expected (Macaroni Kid, Mommy Poppins, KidsOutAndAbout block scrapers). Tier 1 library APIs and Eventbrite are the reliable high-volume sources.

---

## Session 13 (interrupted) — 2026-03-18
**Theme:** Homepage V2 components, image sourcing expansion (Unsplash + Pexels), API/Lambda fixes, Terraform cleanup

> Session cut off mid-way by power outage. All changes written to disk, uncommitted at time of outage.

### Homepage V2 — New Components
Session 11 committed the page shell (Header, Footer, About, Pokémon, Privacy), but the homepage section components were built here:
- `HeroSearch.tsx` — `'use client'`; Airbnb-style Location/Date/Age Group selects, quick filter pills (Today/Weekend/Free), Mon–Sun weekly calendar strip, social proof row
- `WeekendEventsSection.tsx` — `'use client'`; Sat/Sun tab toggle, ❤️ save buttons (useState Set), ⭐ Editor's Pick amber badge on first card each day
- `FreeEventsSection.tsx` — green-themed free events spotlight; SEO H2 targeting "free things to do with kids northern virginia"
- `CityStripsSection.tsx` — 4 city strips (Reston, Fairfax, Arlington, Leesburg); compact event rows; "See all events in [City] →" links
- `NewsletterForm.tsx` — `'use client'`; 4-state machine (idle/loading/success/error); POSTs JSON to `NEXT_PUBLIC_API_URL/newsletter/subscribe`
- `error.tsx`, `global-error.tsx`, `not-found.tsx` — all required for App Router static export
- `page.tsx` updated to import and use all new components

### Image Sourcing — 5-Step Cascade (`services/image-gen/sourcer.py`)
Expanded from 3-step to 5-step priority cascade:
1. Scraped image URL on event (existing)
2. Google Places Photos for venue (existing)
3. **NEW — Unsplash API** (`UNSPLASH_ACCESS_KEY`): keyword-matched free stock photo (landscape orientation, safe content filter, 50 req/hr free tier)
4. **NEW — Pexels API** (`PEXELS_API_KEY`): free stock fallback (unlimited, large2x ~1200px wide)
5. AI generation — Imagen 3 → DALL-E 3 (last resort only)

Added `_build_search_query()`: maps `event_type` → `category` → `tags` to stock photo search terms via three keyword dictionaries (`_EVENT_TYPE_KEYWORDS`, `_CATEGORY_KEYWORDS`, `_TAG_KEYWORDS`). Deals and product drops skip free stock and go directly to AI (branded imagery performs better). Unsplash/Pexels URLs added to `_looks_like_image()` good-patterns list.

### Image Pipeline — Step 0 Upsert (`services/image-gen/handler.py`)
Added `_upsert_event()` as Step 0 in `process_event()`:
- Upserts RawEvent into Supabase (`on_conflict=source_url`) before image generation begins
- Maps RawEvent field names → DB column names (`description` → `full_description`, `location_name` → `venue_name`, `location_address` → `address`)
- Returns the saved DB row with assigned `slug` + `id` — image pipeline uses these for S3 paths and PATCH calls
- Added `_headers()` helper (DRY Supabase auth headers)
- Added SSM bootstrap (`_load_secrets_from_ssm()`) including `UNSPLASH_ACCESS_KEY_PARAM` and `PEXELS_API_KEY_PARAM`
- Added `handler = lambda_handler` alias for Terraform handler config

### API Lambda — Blog Routes + Fixes (`services/api/`)
- `handler.py`: added SSM bootstrap, registered `GET /blog` + `GET /blog/{slug}` routes, added `handler` alias
- `routes/events.py`: fixed DB column name mismatches — `SELECT` now uses `full_description`, `venue_name`, `address`, `location_id` (DB names) instead of aliases that don't exist in the schema
- `routes/pokemon.py`: same fix — `full_description`, `venue_name`, `address`
- `requirements.txt`: added `pydantic[email]` + `email-validator>=2.0`

### Events Scraper Lambda (`services/events-scraper/handler.py`)
Added `_load_secrets_from_ssm()` with mappings for `OPENAI_API_KEY_PARAM`, `SUPABASE_URL_PARAM`, `SUPABASE_KEY_PARAM`, `MEETUP_CLIENT_ID_PARAM`, `MEETUP_SECRET_PARAM`. Called at module init (container warm-up).

### Terraform Cleanup
- `cloudfront.tf`: removed `logging_config` block — conflicts with modern S3 bucket ownership controls (ACL disabled). CloudFront access logging can be enabled manually via AWS Console if needed.
- `cloudwatch.tf`: removed `social_poster` Lambda references from log group, dashboard Lambda invocations/errors/duration metrics; added `region` key to all CloudWatch dashboard widget `properties` (required by API); reformatted multi-attribute blocks for Terraform fmt compliance
- `outputs.tf`: removed `lambda_social_poster_arn` output
- `ssm.tf`: replaced `buffer/access-token` + `buffer/profile-ids` with `ayrshare/api-key`; added `unsplash/access-key` + `pexels/api-key` SSM parameter descriptions

### Next.js / Web Fixes
- `next.config.js`: removed `async headers()` block — `headers()` is not supported with `output: 'export'` (static export); CloudFront handles cache headers in production
- `robots.ts` + `sitemap.ts`: added `export const dynamic = 'force-static'` to both files (prevents dynamic route resolution errors in static export)

### CLAUDE.md
Partially updated on disk (not committed at session end). Updated: "Site is LIVE" note, Buffer → Ayrshare in tech stack, social-poster description, `scripts/` directory entry, cloud Supabase project note, DB column mapping clarification, migration commands (local vs cloud), image pipeline architecture (upsert step + Unsplash/Pexels).

---

## Session 8b — 2026-03-18
**Theme:** Content Generator Lambda + blog system + brand voice blog section + 111 scraper sources

### Content Generator Lambda (`services/content-generator/`)
New Lambda that generates SEO blog posts from live event data. Triggers twice weekly via EventBridge:
- **Thursday 8:00 PM EST** → `weekend` posts ("Things To Do This Weekend in NoVa")
- **Monday 6:00 AM EST** → `week_ahead` posts ("This Week in NoVa with Kids")

**`post_builder.py`** — 5 prompt builders:
1. `weekend` — weekend roundup (main section events Fri–Sun)
2. `location` — city-specific roundups (Reston, Fairfax, Arlington, Leesburg)
3. `free_events` — free events spotlight ("Free Things To Do With Kids This Weekend")
4. `week_ahead` — week-ahead planning post
5. `indoor` — rainy day / indoor activity guide

All prompts inject shared voice rules (brand-voice.md parent-to-parent tone) and FAQ instructions. Idempotency: `post_exists()` checks for existing slug before generating (no duplicate posts on re-runs).

**`prompts.py`** — 328-line prompt library. Each prompt type generates: hook paragraph, logistics blocks (📅📍💰), H2 section headers, insider details rule, FAQ section (4 questions), closing CTA. GPT-4o-mini returns structured Markdown.

**`github_trigger.py`** — after saving new posts, triggers `deploy-frontend` GitHub Actions workflow via repository dispatch API (`POST /repos/owner/repo/dispatches`). Frontend rebuild picks up new blog pages. Requires `GITHUB_TOKEN` with `repo` scope in SSM.

**`handler.py`** — Lambda entry point. Bootstrap secrets from SSM (SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY, GITHUB_TOKEN). Infers trigger type from EventBridge schedule day if not explicitly passed. Calls `build_posts_for_trigger()` → triggers frontend rebuild if posts saved.

**Tests** (`tests/test_post_builder.py`) — 205 lines, 20+ tests: prompt builder output, SSM mock, idempotency check, trigger inference, GitHub trigger call.

### Supabase Migration — Blog Posts Table
`supabase/migrations/20260318000001_create_blog_posts.sql`:
- `blog_posts` table: id, slug (unique), title, post_type, trigger_type, date_range_start, date_range_end, location_filter, content (Markdown), event_ids (uuid[]), published_at, created_at
- RLS: anon can select published posts, service role can insert/update
- GIN index on `event_ids[]` for fast event → post lookups
- Unique constraint: `(post_type, trigger_type, date_range_start, location_filter)` — idempotency key

### Blog API Routes (`services/api/routes/blog.py`)
- `GET /blog` — paginated post listing (20/page), filters: `post_type`, `trigger_type`, `location`; joins event preview data (slug, title, image_url, start_at)
- `GET /blog/{slug}` — single post with full content + joined event objects for EventCard grid

### Blog Frontend Pages (`apps/web/src/app/blog/`)
- `blog/page.tsx` — listing page; server component; metadata; Suspense skeleton; grid of PostCard components
- `blog/[slug]/page.tsx` — detail page; `generateStaticParams` from `/blog` API; `generateMetadata`; Article + BreadcrumbList + per-event Event JSON-LD schemas; minimal Markdown renderer (converts GPT output headings/bold/lists/links to HTML); EventCard grid for events referenced in post; social share buttons; internal links back to `/events`
- `src/types/blog.ts` — BlogPost, PostCard, BlogListResponse TypeScript types
- `src/lib/api.ts` updated — `getBlogPosts()`, `getBlogPost()` client functions

### Brand Voice Updates (`skills/brand-voice.md`)
Added 328-line blog voice section (Section 7 onward):
- **Core principle:** "The most organized parent in the neighborhood Facebook group" — peer, not press release
- **POV rules:** second person ("you/your kids"), "we" sparingly, never third-person ("parents should...")
- **Hook paragraph rules:** 2–3 sentence max; must acknowledge Saturday situation, frame the weekend, or lead with the best thing; 4 approved hook archetypes + 3 rejected examples
- **Event blurb format:** logistics block (📅📍💰) + 3–5 sentence blurb; insider detail rule (2–3 per post minimum; skip rather than fabricate)
- **Enthusiasm calibration table:** approved vs rejected phrases; earn enthusiasm with specificity
- **Tone by post type:** weekend/free/date-specific/location/rainy-day/week-ahead each with hook energy, blurb length, humor, insider tip count
- **Writing craft — sounds human, not AI:** em dash usage, sentence variety rules, contractions always, AI phrases to never use (Furthermore/Additionally/It's worth noting/etc.)
- **Blog UX (mobile-first):** 2–3 sentence paragraphs, logistics blocks as scan anchors, H2 headers every 4–6 events, jump nav for 8+ events, one CTA every 5–6 events
- **GEO + backlink optimization:** why logistics blocks get LLM citations, why specificity drives backlinks, FAQ section required on every post
- **AI generation prompt reference:** full system prompt to inject into GPT-4o-mini calls

### Scraper Sources — 111 Total (`services/events-scraper/config/sources.json`)
Expanded from 59 → 111 Tier 2 sources (+52 new). New sources added:
- 5 Macaroni Kid regional editions (Fairfax, Loudoun, Arlington, Prince William, Reston/Herndon)
- Mommy Poppins DC, Kids Out and About DC/Northern Virginia
- 11 additional Patch hyperlocal city pages
- Community reporters: Reston Patch, Burke Patch, Centreville Patch, Manassas Patch
- Arts venues: Workhouse Arts Center, ArtSpace Herndon, McLean Community Center
- 5 NPS / state park sites (Manassas National Battlefield, Shenandoah, Prince William Forest)
- Town event pages: Town of Herndon, Town of Vienna, City of Falls Church, Town of Leesburg
- Shopping center event calendars: Dulles Town Center, Loudoun Station, One Loudoun, Fair Oaks

### Competitor Analysis (`docs/competitor-analysis.md`)
Full 389-line competitive analysis: Mommy Poppins, Macaroni Kid, DC Metro Moms, Eventbrite, Patch. Covers SEO gaps, content differentiation, monetization comparison, NovaKidLife competitive moats (Pokémon TCG niche, real-time scraping, GEO optimization, local specificity).

### Terraform — Content Generator Infrastructure (`infra/terraform/`)
- `lambda.tf` updated: content-generator Lambda function, IAM role + policy (Supabase, SSM, EventBridge invoke)
- `eventbridge.tf`: 2 new rules — `content-generator-weekend` (Thu 8pm EST `cron(0 0 ? * FRI *)`) and `content-generator-week-ahead` (Mon 6am EST `cron(0 11 ? * MON *)`)
- `variables.tf` updated: `github_token_param` + `github_repo_owner` + `github_repo_name` variables

### CI/CD Workflow Fixes (`.github/workflows/deploy-api.yml`)
Fixed Lambda function names to match actual deployed names: `novakidlife-prod-api`, `novakidlife-prod-events-scraper`, `novakidlife-prod-image-gen`, `novakidlife-prod-content-generator`. (Commit `3241cb1`)

---

## Session 11 — 2026-03-16
**Theme:** SEO infrastructure, skills expansion, Buffer → Ayrshare swap, V2 homepage redesign

### Skills & Infrastructure
Expanded `seo-geo.md` to Fortune 100 level (13 sections covering every SEO/GEO dimension). Created `local-seo.md` from scratch — complete 3-pillar local ranking playbook, 4-tier citation system, GBP setup templates, outreach email scripts, Pokémon TCG niche SEO strategy, 12-month timeline. Created `qa-build.md` — pre-build checklist with all Next.js 15 static export gotchas so the iterative fix-run-fix-run loop never happens again.

**Buffer → Ayrshare:** Buffer removed public API access for new users after Session 8. Rewrote `buffer_client.py` as `AyrshareClient` using Ayrshare API (`POST /api/post`, Bearer token, platforms array). Removed profile ID lookup logic — Ayrshare doesn't need it. Updated `handler.py` and `ssm.py`. SSM parameter path: `/novakidlife/ayrshare/api-key`.

Made initial git commit of all 8 sessions' work (repo had been written directly to disk with no commits). Added `.gitattributes` for LF normalization on Windows first.

### New Pages
- `about/page.tsx` — E-E-A-T signals: mission, 59+ named sources, coverage area, always-free commitment
- `privacy-policy/page.tsx` — minimal policy, noindexed
- `pokemon/page.tsx` — full Pokémon TCG hub with ItemList JSON-LD, event type cards, 5 LGS cards

### New Components
- `Header.tsx` — sticky, amber/sage split logo, Events + Pokémon TCG nav, Find Events CTA
- `Footer.tsx` — dark sage, social icons (Twitter/Instagram/Facebook), 4-county coverage, site links
- `NewsletterForm.tsx` — `'use client'`, 4-state machine (idle/loading/success/error), POSTs JSON to API
- `HeroSearch.tsx` — `'use client'`, Location/Date/Age Group selects + Find Events, quick filter pills (Today/Weekend/Free), weekly Mon–Sun calendar strip with placeholder counts, social proof row
- `WeekendEventsSection.tsx` — `'use client'`, Sat/Sun tab toggle, ❤️ heart save buttons (useState Set), ⭐ Editor's Pick amber badge on first card each day
- `FreeEventsSection.tsx` — green-themed free events spotlight, SEO H2 targeting "free things to do with kids northern virginia"
- `CityStripsSection.tsx` — 4 city strips (Reston, Fairfax, Arlington, Leesburg), compact event rows, "See all events in [City] →" links
- `not-found.tsx`, `error.tsx`, `global-error.tsx` — all required for App Router static export

### Homepage V2
Replaced Session 1 design system demo with real homepage. Ten sections in order: gradient hero with HeroSearch embedded → stats bar (59+ sources, 4 counties, Free, Daily) → browse by category (6 cards) → WeekendEventsSection → browse by age (4 age group cards) → FreeEventsSection → CityStripsSection → editorial blog (Rainy Day Activities featured + 2 more) → coverage area (15 clickable city chips) → newsletter. All event data is placeholder — wired to live API in Session 12.

### Build Fixes
All documented in `skills/qa-build.md`. Key fixes: Next.js 15 `params` must be `Promise<{slug}>` and awaited; `generateStaticParams` must return at least one entry (`_placeholder` fallback); `notFound()` must be outside try/catch; `robots.ts`/`sitemap.ts` need `export const dynamic = 'force-static'`; `AbortSignal.timeout(8000)` on all API fetches prevents build hangs; two-pass build required (first pass creates chunk cache for Pages Router, second pass builds clean).

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
