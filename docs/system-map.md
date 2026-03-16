# NovaKidLife — Master System Map

> One-stop reference for the entire platform. Read this first in any new session.
> Last updated: 2026-03-15 | Sessions complete: 1–7, 9 of 12

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USERS (Parents / Caregivers)                      │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │ HTTPS
                              ┌──────▼───────┐
                              │  CloudFront  │  CDN + SSL termination
                              └──────┬───────┘
                    ┌────────────────┼────────────────┐
                    ▼                ▼                 ▼
             ┌────────────┐  ┌────────────┐   ┌──────────────┐
             │  S3 (web)  │  │ S3 (media) │   │ API Gateway  │
             │ Static HTML│  │ WebP images│   │ REST API     │
             └─────┬──────┘  └─────┬──────┘   └──────┬───────┘
                   │               │                  │
              Next.js SSG     CDN media URLs    ┌─────▼──────────┐
           (apps/web/out/)  media.novakidlife.com│  API Lambda    │
                                                │ (services/api) │
                                                └─────┬──────────┘
                                                      │
                                              ┌───────▼────────┐
                                              │    Supabase    │
                                              │  PostgreSQL    │
                                              │  + pgvector    │
                                              └───────┬────────┘
                                                      │
            ┌─────────────────────────────────────────┘
            │         BACKGROUND PIPELINE (automated)
            ▼
    ┌──────────────────┐
    │  EventBridge     │  Daily 6am EST trigger
    └────────┬─────────┘
             ▼
    ┌──────────────────┐
    │ events-scraper   │  59 sources, 4 tiers
    │    Lambda        │
    └────────┬─────────┘
             ▼
    ┌──────────────────┐
    │   SQS Queue      │  novakidlife-events-queue
    └──┬───────────────┘
       │           │
       ▼           ▼
┌──────────┐  ┌──────────────┐
│image-gen │  │ social-poster│
│  Lambda  │  │    Lambda    │
└────┬─────┘  └──────┬───────┘
     │               │
     ▼               ▼
  S3 media        Buffer API
  (WebP uploads)  (scheduled posts)
```

---

## Component Inventory

### Frontend — `apps/web/`

| File / Directory | Purpose | Status |
|-----------------|---------|--------|
| `src/app/layout.tsx` | Root layout, fonts, global SEO metadata, title template | ✅ |
| `src/app/page.tsx` | Homepage (design system demo) + WebSite + LocalBusiness JSON-LD | ✅ |
| `src/app/globals.css` | CSS custom properties (color tokens) | ✅ |
| `src/app/sitemap.ts` | Dynamic sitemap.xml — fetches all slugs from /sitemap API | ✅ |
| `src/app/robots.ts` | robots.txt — allows all crawlers + explicit AI bot list | ✅ |
| `src/app/events/page.tsx` | Events listing — server component, metadata, Suspense wrapper | ✅ |
| `src/app/events/EventsClient.tsx` | URL-synced filters, semantic search, pagination | ✅ |
| `src/app/events/[slug]/page.tsx` | Event detail — generateStaticParams + full SEO layout | ✅ |
| `src/components/BlurImage.tsx` | LQIP blur-up image, explicit dimensions (CLS prevention) | ✅ |
| `src/components/EventCard.tsx` | Event card with date, cost badge, tags | ✅ |
| `src/components/EventCardSkeleton.tsx` | Pulse skeleton placeholder | ✅ |
| `src/components/EventGrid.tsx` | 1→2→3 responsive grid, LCP priority on first 3 | ✅ |
| `src/components/SearchBar.tsx` | 500ms debounce, spinner, clear button | ✅ |
| `src/components/FilterBar.tsx` | Date presets, category, free toggle, result count | ✅ |
| `src/components/Pagination.tsx` | Ellipsis-aware page numbers, aria-current | ✅ |
| `src/components/EmptyState.tsx` | No-results state with clear filters CTA | ✅ |
| `src/components/Breadcrumbs.tsx` | Nav trail with chevrons, aria-current | ✅ |
| `src/components/EventJsonLd.tsx` | Event + BreadcrumbList + FAQPage JSON-LD scripts | ✅ |
| `src/components/RelatedEvents.tsx` | 3 related events by section + tags (client fetch) | ✅ |
| `src/components/ShareButtons.tsx` | Copy link, Twitter/X, Facebook share | ✅ |
| `src/lib/api.ts` | Typed API client — all endpoints | ✅ |
| `src/types/events.ts` | TypeScript interfaces: Event, Category, Location, etc. | ✅ |
| `src/types/supabase.ts` | Generated Supabase types | ✅ |
| `public/llms.txt` | LLM crawler file for GEO (ChatGPT, Perplexity, Claude, etc.) | ✅ |
| `public/fonts/` | Self-hosted woff2 font files | ✅ |
| `next.config.js` | output: 'export', trailingSlash: true | ✅ |

**Pages not yet built:**
| Page | Session | Notes |
|------|---------|-------|
| `/pokemon` hub | 8+ | Listing of Pokémon TCG events + set drops |
| `/pokemon/events/[slug]` | 8+ | Pokemon event detail (reuse [slug] layout) |
| `/pokemon/drops` | 8+ | Set releases + NoVa retailer matrix |
| Homepage (real) | 12 | Replace design system demo at launch |

---

### API — `services/api/`

| File | Purpose | Status |
|------|---------|--------|
| `handler.py` | Lambda entry point, 15 routes registered | ✅ |
| `router.py` | Lightweight path router (regex params, CORS, 500 catch) | ✅ |
| `models.py` | SearchRequest, NewsletterSubscribeRequest, event_to_response(), paginated() | ✅ |
| `db.py` | Cached Supabase client shared by all routes | ✅ |
| `routes/events.py` | GET /events (7 filters), /featured, /upcoming, /[slug], POST /search | ✅ |
| `routes/pokemon.py` | GET /pokemon/events, /drops, /retailers | ✅ |
| `routes/categories.py` | GET /categories (with event counts) | ✅ |
| `routes/locations.py` | GET /locations (with event counts) | ✅ |
| `routes/newsletter.py` | POST /newsletter/subscribe | ✅ |
| `routes/sitemap.py` | GET /sitemap (slug arrays by section for Next.js build) | ✅ |
| `routes/admin.py` | POST /admin/events/trigger-scrape, GET /admin/health/detailed | ✅ |
| `tests/test_router.py` | 21 unit tests (router, models, CORS, column mapping) | ✅ |

**API endpoint map:**
```
GET  /health
GET  /events                    ?section, event_type, category, location_id,
                                 start_date, end_date, tags, is_free, limit, offset
GET  /events/featured           ?section, limit
GET  /events/upcoming           ?section, limit
GET  /events/{slug}
POST /events/search             { query, section, limit }
GET  /pokemon/events            ?format, limit, offset
GET  /pokemon/drops             ?limit, offset
GET  /pokemon/retailers         ?type
GET  /categories
GET  /locations
POST /newsletter/subscribe      { email }
GET  /sitemap
POST /admin/events/trigger-scrape   [X-Api-Key required]
GET  /admin/health/detailed         [X-Api-Key required]
```

---

### Events Scraper — `services/events-scraper/`

| Component | Purpose | Status |
|-----------|---------|--------|
| `handler.py` | Lambda entry — runs all tiers, reports stats | ✅ |
| `scrapers/base.py` | BaseScraper: httpx retry, JSON-LD extraction, HTML cleaning | ✅ |
| `scrapers/models.py` | RawEvent dataclass, EventType + DealCategory enums | ✅ |
| `scrapers/publisher.py` | SQS batch publisher (10/batch) | ✅ |
| `scrapers/tier1/` | Fairfax/Loudoun/Arlington library APIs + Eventbrite + Meetup | ✅ |
| `scrapers/tier2/` | AITier2Scraper: URL → gpt-4o-mini → RawEvent | ✅ |
| `scrapers/tier3/` | KrazyCouponLady, Hip2Save, Google News RSS deals | ✅ |
| `scrapers/pokemon/events_scraper.py` | Play! Pokémon + 5 NoVa LGS | ✅ |
| `scrapers/pokemon/drops_scraper.py` | Release calendar + 15-store retailer matrix | ✅ |
| `config/sources.json` | All 59 sources — add Tier 2 here, zero code | ✅ |

**Source breakdown:**
```
Tier 1 (5):  Fairfax Library, Loudoun Library, Arlington Library, Eventbrite, Meetup API
Tier 2 (46): 11 Patch cities, 7 local news, 6 gov/parks, 10 venues, + more
Tier 3 (5):  KrazyCouponLady, Hip2Save, Google News RSS × 3
Pokémon (3): Play! Pokémon locator, 5 LGS websites, Google News RSS
```

---

### Image Generation — `services/image-gen/`

| File | Purpose | Status |
|------|---------|--------|
| `prompts.py` | WEBSITE_PROMPTS (14), SOCIAL_PROMPTS (14), POKEMON_PROMPTS (7) | ✅ |
| `sourcer.py` | Scraped URL → Google Places Photos → None | ✅ |
| `generator.py` | Imagen 3 (primary) → DALL-E 3 (fallback) | ✅ |
| `enhancer.py` | Pillow warm grade: warmth, contrast, saturation, vignette | ✅ |
| `processor.py` | All WebP variants + LQIP base64 + blurhash | ✅ |
| `alt_text.py` | gpt-4o-mini → ≤125 char SEO alt text | ✅ |
| `uploader.py` | S3 upload, 1-year cache headers, skip-if-exists | ✅ |
| `handler.py` | SQS orchestrator — full pipeline + Supabase PATCH | ✅ |

**Output variants per event:**
```
hero.webp      1200×675   Website hero image (LCP)
hero-md.webp    800×450   srcset medium
hero-sm.webp    400×225   srcset small
card.webp       600×400   Event card
og.webp        1200×630   OpenGraph / Twitter card
social.webp   1080×1080   Social post (always AI illustration)
+ LQIP data URL (20×11 base64) + blurhash string
```

---

### Social Poster — `services/social-poster/` ⬜ Session 8

| Component | Purpose |
|-----------|---------|
| `handler.py` | Lambda SQS trigger |
| `buffer_client.py` | Buffer API wrapper |
| `copy_builder.py` | Platform-specific copy from event data |
| `scheduler.py` | Optimal posting time calculator |

---

### Database — `supabase/`

**All 11 migrations (all applied ✅):**
```
20260313000001  pgvector + uuid-ossp extensions
20260313000002  locations table (15 NoVa locations seeded)
20260313000003  categories table (15 categories seeded)
20260313000004  events table (34 cols, RLS, 10 indexes, ivfflat vector index)
20260313000005  newsletter_subs table + RLS
20260313000006  fix newsletter RLS (email regex, not true)
20260314000001  deal fields (event_type, brand, discount_description, deal_category)
20260314000002  image SEO fields (alt, width, height, blurhash, url variants)
20260314000003  section field (main | pokemon routing)
20260314000004  search_events() RPC (pgvector cosine similarity)
20260314000005  fix event_type constraint (adds pokemon_tcg + product_drop)
```

**Critical DB note — column name mapping:**
```
DB column          → API response / TypeScript type
venue_name         → location_name
address            → location_address
full_description   → description
short_description  → (stripped, not sent to frontend)
```
Handled by `event_to_response()` in `services/api/models.py`.

---

### Infrastructure — `infra/terraform/` ✅ Session 9

| File | Purpose | Status |
|------|---------|--------|
| `main.tf` | Provider config (aws ~>5.0), S3 backend, DynamoDB lock, us-east-1 alias provider | ✅ |
| `variables.tf` | All input variables (region, domains, cert ARNs, Lambda sizing, alarm config) | ✅ |
| `s3.tf` | novakidlife-web + novakidlife-media + novakidlife-tfstate + DynamoDB lock table | ✅ |
| `cloudfront.tf` | 2 distributions (web + media CDN), OAC, cache policies, CloudFront Function (URL rewrite) | ✅ |
| `lambda.tf` | 5 Lambda functions + IAM roles (api, events-scraper, image-gen, social-poster, scheduler) | ✅ |
| `api_gateway.tf` | Regional REST API, /{proxy+} catch-all, CORS OPTIONS, prod stage, custom domain | ✅ |
| `sqs.tf` | 4 queues (events-queue + events-dlq + social-queue + social-dlq), queue policies | ✅ |
| `eventbridge.tf` | Daily scraper rule cron(0 11 * * ? *) → events-scraper Lambda | ✅ |
| `ssm.tf` | 14 SecureString placeholders under /novakidlife/* | ✅ |
| `cloudwatch.tf` | SNS topic, Lambda log groups, error/duration/DLQ/5xx alarms, ops dashboard | ✅ |
| `outputs.tf` | CloudFront domains, distribution IDs, API URLs, queue ARNs, DNS records to create | ✅ |

**Bootstrap (one-time before `terraform init`):**
```bash
aws s3api create-bucket --bucket novakidlife-tfstate --region us-east-1
aws s3api put-bucket-versioning --bucket novakidlife-tfstate \
  --versioning-configuration Status=Enabled
aws dynamodb create-table --table-name novakidlife-tflock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region us-east-1
```

**ACM certs (required for custom domains — create in us-east-1):**
```bash
aws acm request-certificate --domain-name novakidlife.com \
  --subject-alternative-names "*.novakidlife.com" \
  --validation-method DNS --region us-east-1
```
Then pass ARN as `web_acm_certificate_arn` and `api_acm_certificate_arn` variables.

---

### CI/CD — `.github/workflows/` ⬜ Session 10

| Workflow | Trigger | Action |
|---------|---------|--------|
| `test.yml` | PR to main | pytest + TypeScript type-check |
| `deploy-frontend.yml` | Push to main | npm build → S3 sync → CloudFront invalidation |
| `deploy-api.yml` | Push to main | pip install → zip → Lambda update × 5 |
| `lighthouse.yml` | PR to main | Lighthouse CI — enforce 90+ scores |
| `terraform.yml` | Push to main | fmt + validate + plan (no auto-apply) |

---

## Data Flow Diagrams

### Event Lifecycle
```
[Source website]
      │
      ▼
[Scraper Lambda]  ← EventBridge 6am daily
  extracts RawEvent
      │
      ▼
[SQS: events-queue]
      │
      ├──► [Image Gen Lambda]
      │      source → generate → enhance → process → upload → DB PATCH
      │      (sets status = 'enriched')
      │
      └──► [Content Enrichment — future]
             generate descriptions → DB PATCH
             (sets status = 'published')
      │
      ▼
[Supabase events table]  status = 'published'
      │
      ▼
[Next.js static build]   generateStaticParams fetches all slugs
      │                   → builds /events/[slug] HTML files
      ▼
[S3 + CloudFront]   HTML served globally
      │
      ▼
[Social Poster Lambda]   SQS trigger on new published events
      │                   generates platform copy → Buffer API
      ▼
[Buffer]   Schedules posts for optimal times
```

### Search Flow
```
User types in SearchBar
      │ (500ms debounce)
      ▼
POST /events/search  { query: "storytime fairfax toddler" }
      │
      ▼
[API Lambda]
  OpenAI text-embedding-3-small → vector(1536)
      │
      ▼
[Supabase search_events() RPC]
  cosine similarity via pgvector ivfflat index
  OPERATOR(extensions.<=>) syntax (search_path = '')
      │
      ▼
[Results ranked by similarity]  → frontend
```

---

## Configuration Reference

### Environment Variables

**`apps/web/.env.local`**
```
NEXT_PUBLIC_API_URL=https://api.novakidlife.com
NEXT_PUBLIC_SITE_URL=https://novakidlife.com
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321     ← local dev only
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_...
```

**`services/*/.env`** (local dev — SSM in production)
```
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=sb_secret_...
OPENAI_API_KEY=sk-...
GOOGLE_PROJECT_ID=...
GOOGLE_LOCATION=us-central1
GOOGLE_SERVICE_ACCOUNT_JSON={...}
GOOGLE_PLACES_API_KEY=...
MEDIA_BUCKET_NAME=novakidlife-media
MEDIA_CDN_URL=https://media.novakidlife.com
MEETUP_CLIENT_ID=...             ← register at meetup.com/api/oauth/list/
MEETUP_CLIENT_SECRET=...
BUFFER_ACCESS_TOKEN=...
BUFFER_PROFILE_IDS=id1,id2,id3
```

**SSM Parameter Store paths (production)**
```
/novakidlife/supabase/url
/novakidlife/supabase/service-key
/novakidlife/openai/api-key
/novakidlife/google/project-id
/novakidlife/google/service-account-json
/novakidlife/google/places-api-key
/novakidlife/media/bucket-name
/novakidlife/media/cdn-url
/novakidlife/meetup/client-id
/novakidlife/meetup/client-secret
/novakidlife/buffer/access-token
/novakidlife/buffer/profile-ids
/novakidlife/admin/api-key
```

---

## Skills Reference (complete)

| Skill | Purpose |
|-------|---------|
| `deploy-frontend.md` | S3 deploy + CloudFront invalidation |
| `deploy-api.md` | Lambda package + publish |
| `db-migrate.md` | Supabase migrations |
| `add-component.md` | React component scaffolding |
| `add-lambda.md` | Lambda function scaffolding |
| `generate-event.md` | AI event generation |
| `generate-image.md` | Full image pipeline |
| `post-social.md` | Buffer API posting (technical) |
| `scrape-events.md` | Trigger + monitor scraper |
| `terraform-plan.md` | Safe Terraform plan |
| `terraform-apply.md` | Gated Terraform apply |
| `seed-db.md` | Seed Supabase with test data |
| `test-api.md` | API endpoint testing |
| `check-lighthouse.md` | Lighthouse CI |
| `monitor.md` | System health checks |
| `seo-geo.md` | SEO + GEO standards (apply every frontend session) |
| `social-strategy.md` | Platform strategy: Twitter algorithm, Instagram, Facebook |
| `brand-voice.md` | Tone, voice, language rules, visual identity |
| `content-generation.md` | Templates for all content types |
| `autonomous-agents.md` | Agent architecture, schedules, failure handling |
| `mcp-builder.md` | Building MCP servers for NovaKidLife |
| `skill-creator.md` | How to create new skills |

---

## Session Roadmap

| # | Focus | Status | Key Deliverables |
|---|-------|--------|-----------------|
| 1 | Foundation | ✅ | Repo, Next.js 15, design system, 15 skills |
| 2 | Database | ✅ | Supabase, 11 migrations, pgvector, RLS |
| 3 | Scraper | ✅ | 3-tier, 59 sources, deal types |
| 4 | Image Gen | ✅ | Two pipelines, all WebP variants, LQIP |
| 4b | Pokémon | ✅ | Section routing, scrapers, retailer matrix |
| 5 | API | ✅ | 15 endpoints, pgvector search, 21 tests |
| 6 | Events Listing | ✅ | 8 components, URL state, search |
| 7 | Event Detail + SEO | ✅ | Detail page, JSON-LD, sitemap, robots, llms.txt |
| **8** | **Social Poster** | ⬜ | Buffer Lambda, platform copy builder |
| **9** | **Terraform** | ✅ | Full IaC, all AWS resources |
| **10** | **CI/CD** | ⬜ | 5 GitHub Actions workflows |
| **11** | **SEO + Performance** | ⬜ | Lighthouse 90+, audit fixes |
| **12** | **Launch** | ⬜ | DNS, SSL, monitoring, go-live |

---

## Key Technical Decisions (ADR Summary)

| Decision | Choice | Reason |
|----------|--------|--------|
| Static export | `output: 'export'` | No server cost, CloudFront serves globally |
| Vector search | pgvector in Supabase | No separate vector DB needed |
| Image AI | Imagen 3 + DALL-E 3 fallback | Imagen quality; DALL-E as safety net |
| Image format | WebP + LQIP + blurhash | Fastest load + no layout shift |
| Social | Buffer API | Handles scheduling + multi-platform |
| IaC | Terraform | State in S3, reproducible infra |
| Local DB | Supabase Docker | Free tier avoidance until launch (ADR-008) |
| pgvector operators | `OPERATOR(extensions.<=>)` syntax | Required when `search_path = ''` |
