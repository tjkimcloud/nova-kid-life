# NovaKidLife

> **Northern Virginia's family events discovery platform** — live at [novakidlife.com](https://novakidlife.com)

A production, monetized web application that aggregates family-friendly events, deals, and Pokémon TCG activities across Northern Virginia. Built end-to-end as a solo full-stack + cloud engineering project.

---

## What It Does

Parents in Northern Virginia search for things to do with their kids every week. NovaKidLife automatically scrapes **111 sources daily** — library APIs, local news sites, government parks pages, event platforms, and deal blogs — enriches each event with AI-generated images, and serves everything through a fast static site with semantic search.

**Key features:**
- Browse and filter 15 event categories across 15 NoVa locations
- AI-powered semantic search (vector similarity via pgvector)
- Pokémon TCG hub: local game store events, product drop calendar, retailer guide
- Auto-generated SEO blog content (5 post types, published 2×/week)
- Newsletter subscription

---

## Architecture

```mermaid
flowchart TD
    Users(["👨‍👩‍👧 Users\n(Parents / Caregivers)"])

    subgraph AWS ["☁️ AWS"]
        CF["CloudFront\nCDN + ACM wildcard SSL"]
        S3Web["S3 — Static Web\nNext.js SSG output"]
        S3Media["S3 — Media\nWebP images"]
        APIGW["API Gateway\napi.novakidlife.com"]
        APILambda["API Lambda\nPython 3.12 · 15 routes"]
        EB["EventBridge\nCron scheduler"]
        ScraperLambda["events-scraper Lambda\n111 sources · 3 tiers + Pokémon"]
        SQS["SQS\nevents-queue"]
        ImageLambda["image-gen Lambda\nSourcer → AI → WebP"]
        ContentLambda["content-generator Lambda\n5 post types · 2×/week"]
    end

    subgraph Supabase ["🗄️ Supabase"]
        DB["PostgreSQL\n+ pgvector"]
    end

    GH["GitHub Actions\ndeploy-frontend workflow"]

    Users -->|HTTPS| CF
    CF --> S3Web
    CF --> S3Media
    CF --> APIGW
    APIGW --> APILambda
    APILambda --> DB

    EB -->|Daily 6am EST| ScraperLambda
    EB -->|Thu 8pm + Mon 6am EST| ContentLambda

    ScraperLambda --> SQS
    SQS --> ImageLambda
    ImageLambda --> S3Media
    ImageLambda -->|PATCH images| DB

    ContentLambda -->|Save posts| DB
    ContentLambda -->|Trigger deploy| GH
    GH -->|npm build → S3 sync| S3Web
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (static export) · TypeScript · Tailwind CSS 3.4 |
| Hosting | AWS S3 + CloudFront (CDN + ACM wildcard cert) |
| API | AWS API Gateway + Lambda (Python 3.12) |
| Database | Supabase (PostgreSQL + pgvector) |
| Queue | AWS SQS + DLQ |
| Scheduler | AWS EventBridge (cron rules) |
| AI — Images | Google Imagen 3 (primary) · DALL-E 3 (fallback) |
| AI — Content | OpenAI gpt-4o-mini (blog generation, alt text, scraping) |
| AI — Search | OpenAI text-embedding-3-small → pgvector cosine similarity |
| Image Stock | Google Places → Unsplash → Pexels cascade (AI fallback) |
| IaC | Terraform (S3 backend · DynamoDB state lock) |
| CI/CD | GitHub Actions (5 workflows) |
| Secrets | AWS SSM Parameter Store (18+ SecureString params) |

---

## Event Data Pipeline

### 3-Tier Scraper + Pokémon Module

```
Tier 1 (5 sources)   → Structured APIs
                         Fairfax Library · Loudoun Library · Arlington Library
                         Eventbrite API · Meetup API

Tier 2 (98 sources)  → AI-Extracted (zero code to add new sources)
                         Patch city pages · local news · gov/parks sites
                         museum sites · venue blogs
                         Config-driven: add URL to config/sources.json only

Tier 3 (5 sources)   → Deal monitors
                         KrazyCouponLady · Hip2Save · Google News RSS ×3

Pokémon (3 modules)  → Play! Pokémon locator · 5 NoVa LGS websites
                         Product drop calendar · 15-store retailer matrix

Output → SQS → Image Gen Lambda
```

### Image Pipeline

Two separate pipelines run per event:

```mermaid
flowchart LR
    subgraph Website ["🖼️ Website Images (sourced → AI fallback)"]
        direction LR
        URL["Scraped URL"] --> GP["Google Places"]
        GP -->|hit| Grade
        GP -->|miss| US["Unsplash"]
        US -->|hit| Grade
        US -->|miss| PX["Pexels"]
        PX -->|hit| Grade
        PX -->|miss| IM["Imagen 3\n(AI fallback)"]
        IM --> Grade["Pillow warm grade\n(warmth · contrast · vignette)"]
        Grade --> WP["WebP variants\nhero · card · og · srcset"]
        WP --> LQIP["LQIP base64\n+ blurhash"]
        LQIP --> DB[("Supabase PATCH")]
    end

    subgraph Social ["📱 Social Images (always AI)"]
        direction LR
        Prompt["Category prompt library"] --> IM2["Imagen 3"]
        IM2 --> SW["social.webp\n1080×1080"]
    end
```

### Semantic Search

```mermaid
flowchart LR
    Q["User query"] --> EMB["OpenAI\ntext-embedding-3-small"]
    EMB --> VEC["vector 1536 dims"]
    VEC --> RPC["Supabase\nsearch_events() RPC"]
    RPC --> PGV["pgvector ivfflat index\ncosine similarity"]
    PGV --> RES["Ranked results"]
```

---

## API Endpoints

Deployed on `api.novakidlife.com` (API Gateway + Lambda):

```
GET  /health
GET  /events                 ?section, event_type, category, location_id,
                              start_date, end_date, tags, is_free, limit, offset
GET  /events/featured        ?section, limit
GET  /events/upcoming        ?section, limit
GET  /events/{slug}
POST /events/search          { query, section, limit }
GET  /pokemon/events         ?format, limit, offset
GET  /pokemon/drops          ?limit, offset
GET  /pokemon/retailers      ?type
GET  /categories
GET  /locations
POST /newsletter/subscribe   { email }
GET  /sitemap
POST /admin/events/trigger-scrape   [X-Api-Key]
GET  /admin/health/detailed         [X-Api-Key]
```

---

## Database Schema

Supabase (PostgreSQL) with pgvector extension:

| Table | Purpose |
|---|---|
| `events` | All events, deals, Pokémon — 34 columns, RLS, 10 indexes, ivfflat vector index |
| `categories` | 15 categories |
| `locations` | 15 NoVa locations (seeded) |
| `newsletter_subs` | Email subscribers — RLS enforced |
| `blog_posts` | AI-generated content, Markdown, linked event IDs |

**Event types:** `event` · `deal` · `birthday_freebie` · `amusement` · `seasonal` · `pokemon_tcg` · `product_drop`

---

## Infrastructure (Terraform)

All AWS resources defined as code in `infra/terraform/`:

| Resource | Purpose |
|---|---|
| S3 (×3) | Static web hosting · media CDN bucket · Terraform state |
| CloudFront (×2) | Web distribution + media CDN, OAC, CloudFront Function URL rewrite |
| API Gateway | Regional REST API, `/{proxy+}` catch-all, custom domain |
| Lambda (×4) | api · events-scraper · image-gen · content-generator |
| SQS (×4) | events-queue + DLQ · social-queue + DLQ |
| EventBridge | Daily scraper cron · Thu/Mon content-gen rules |
| SSM (×18+) | All secrets as SecureString under `/novakidlife/` prefix |
| CloudWatch | SNS alarms · Lambda log groups · ops dashboard |
| DynamoDB | Terraform state lock table |

State stored in S3 with DynamoDB locking for safe remote operations.

---

## CI/CD (GitHub Actions)

| Workflow | Trigger | What It Does |
|---|---|---|
| `test.yml` | PR to main | pytest + TypeScript type-check |
| `deploy-frontend.yml` | Push to main | `npm run build` → S3 sync → CloudFront invalidation |
| `deploy-api.yml` | Push to main | pip install → zip → Lambda update ×4 |
| `lighthouse.yml` | PR to main | Lighthouse CI — enforce 90+ scores |
| `terraform.yml` | Push to main | fmt + validate + plan (no auto-apply) |

The content-generator Lambda also triggers `deploy-frontend.yml` via the GitHub API after saving new blog posts — so the static site rebuilds automatically with fresh content.

---

## Frontend

Built with **Next.js 15 static export** — zero server cost, served globally from CloudFront.

**Pages:**
- `/` — Homepage: hero search, weekend events, featured events, free events, city strips, blog, newsletter
- `/events` — Full event listing: URL-synced filters, category/date/location/free toggles, pagination
- `/events/[slug]` — Event detail: full SEO layout, JSON-LD (Event + BreadcrumbList + FAQPage), related events, share buttons
- `/blog` — Blog post grid (AI-generated)
- `/blog/[slug]` — Blog detail: Markdown renderer, linked event cards, Article JSON-LD
- `/pokemon` — Pokémon TCG hub: local events, product drops, retailer guide
- `/about` — E-E-A-T authority page

**Key components:**
- `HeroSearch` — Airbnb-style search bar + live day-count calendar strip
- `WeekendEventsSection` — Sat/Sun tab toggle, save buttons, Editor's Pick badge
- `FilterBar` — Date presets, category dropdown, free-only toggle, result count
- `SearchBar` — 500ms debounce, spinner, clear button
- `BlurImage` — LQIP blur-up progressive image loading (CLS prevention)
- `EventJsonLd` — Structured data scripts for SEO

**SEO / GEO:**
- Dynamic `sitemap.xml` (all slugs via API)
- `robots.txt` with explicit AI crawler permissions
- `public/llms.txt` for LLM citation optimization (ChatGPT, Perplexity, Claude)
- JSON-LD structured data on every event and blog page
- OpenGraph + Twitter card meta on all pages

---

## Project Structure

```
nova-kid-life/
├── apps/
│   └── web/                    Next.js 15 frontend
│       └── src/
│           ├── app/            Pages (App Router)
│           ├── components/     UI components
│           ├── lib/            API client
│           └── types/          TypeScript interfaces
├── services/
│   ├── api/                    API Lambda (Python 3.12, 15 routes)
│   ├── events-scraper/         Scraper Lambda (3-tier + Pokémon)
│   ├── image-gen/              Image Gen Lambda (sourcing + AI + WebP)
│   ├── content-generator/      Blog Lambda (5 post types, EventBridge)
│   └── social-poster/          Social Lambda (code preserved, pending Ayrshare)
├── infra/
│   └── terraform/              All AWS resources as IaC
├── supabase/
│   └── migrations/             13 applied migrations
├── scripts/                    Lambda deploy scripts
├── config/
│   └── sources.json            111 scrape sources (Tier 2 config-driven)
├── skills/                     Operational runbooks
└── docs/                       Architecture + system map
```

---

## Key Engineering Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Static export | Next.js `output: 'export'` | Zero server cost — CloudFront serves globally at CDN speed |
| Vector search | pgvector in Supabase | No separate vector database; cosine similarity in existing Postgres |
| Image AI | Imagen 3 → DALL-E 3 fallback | Imagen 3 quality with DALL-E as safety net |
| Image format | WebP + LQIP + blurhash | Maximum load performance, no layout shift |
| Secrets | AWS SSM Parameter Store | All Lambdas load secrets at init — no hardcoded keys anywhere |
| IaC | Terraform | Reproducible infra; state in S3 with DynamoDB lock |
| Scraper config | `config/sources.json` | Add new Tier 2 sources with zero code changes |

---

## Live Site

**[novakidlife.com](https://novakidlife.com)** — CloudFront + ACM wildcard cert + Route 53 DNS

Built and deployed solo across 15 development sessions covering: database design, scraper architecture, AI image pipelines, API development, frontend build, Terraform IaC, CI/CD, SEO optimization, and production launch.
