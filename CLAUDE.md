# NovaKidLife — Claude Code Project Guide

## Autonomous Operation — CRITICAL

**Never ask for permission to proceed.** Execute tasks fully and continuously until done.

- Do NOT ask "should I proceed?", "do you want me to X?", "shall I also Y?", "is that OK?"
- Do NOT present options and wait for a choice — pick the best option and do it
- Do NOT stop after each step to summarize and ask what's next — keep going
- Do NOT ask "yes or no" confirmation questions before taking action
- If a task has multiple sub-steps, complete all of them without pausing
- Only stop and ask if you are **completely blocked** (missing credentials, ambiguous requirement with no reasonable default, destructive irreversible action like deleting prod data)
- When in doubt: act, then report what you did at the end

The user may be away (sleeping, working). Assume full authorization for all work within this project.

### Hard stops — the only 3 things that require explicit approval before proceeding:
1. `terraform apply` — always run `terraform plan` first and show the plan summary. Never apply blindly.
2. Dropping or truncating a database table in production Supabase
3. Deleting an S3 bucket or CloudFront distribution

---

## Project Overview

**NovaKidLife** (novakidlife.com) is a family events discovery platform for Northern Virginia.
Live monetized business + AWS portfolio project.

**Site is LIVE** at https://novakidlife.com — CloudFront + ACM wildcard cert + Route 53 DNS.
Supabase cloud project: `ovdnkgpdgkceulkpwedj`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (static export) + TypeScript + Tailwind CSS 3.4 |
| Hosting | AWS S3 + CloudFront |
| API | AWS API Gateway + Lambda (Python 3.12) |
| Database | Supabase (PostgreSQL + pgvector) |
| Queue | AWS SQS + DLQ |
| Scheduler | AWS EventBridge |
| AI | OpenAI gpt-4o-mini + Imagen 3 / DALL-E 3 |
| Social | Ayrshare API |
| IaC | Terraform (S3 backend, DynamoDB lock) |
| CI/CD | GitHub Actions (5 workflows) |

---

## Design System

Read `DESIGN_SYSTEM.md` before any UI, component, or styling work.
This is the source of truth for all visual decisions — colors, fonts, dark mode, mobile-first rules.
Do not use the old amber/sage palette. Apply Creamsicle Modern tokens only.

---

## Architecture — Critical Context

### Scraper (3-tier + Pokémon)
- **Tier 1:** Structured APIs (libraries, Eventbrite, Meetup)
- **Tier 2:** AI-extracted — add new sources via `config/sources.json` only, zero code
- **Tier 3:** Deal monitors (KrazyCouponLady, Hip2Save, Google News RSS)
- **Pokémon:** Play! Pokémon locator + 5 NoVa LGS + drops calendar
- Output → SQS → image-gen Lambda

### Image Pipeline (two separate pipelines)
- **Website:** sourcer (Google Places → Unsplash → Pexels → AI fallback) → Imagen 3 → Pillow grade → WebP variants
- **Social:** always AI-generated flat illustration, never sourced
- See `skills/generate-image.md` for full SOP

### Site Sections (`section` column)
- `main` → `/events` feed
- `pokemon` → `/pokemon` hub

---

## Database

**Local:** `supabase start` → Studio at http://127.0.0.1:54323
**Cloud:** `supabase link --project-ref ovdnkgpdgkceulkpwedj` then `supabase db push`

### Tables
| Table | Purpose |
|-------|---------|
| `events` | All events + deals + Pokémon |
| `categories` | 15 categories |
| `locations` | 15 NoVa locations |
| `newsletter_subs` | Email subscribers |
| `blog_posts` | AI-generated blog content |

### ⚠️ Critical Column Name Mapping
DB uses: `venue_name` / `address` / `full_description`
API response uses: `location_name` / `location_address` / `description`
Mapping happens in `services/api/models.py` → `event_to_response()`
Always use DB column names in SQL; API names in frontend.

### Event Types
`event` · `deal` · `birthday_freebie` · `amusement` · `seasonal` · `pokemon_tcg` · `product_drop`

---

## Key Commands

```powershell
# ⚠️ PowerShell: use ; not && between commands

# Frontend
cd apps/web ; npm run dev          # localhost:3000
cd apps/web ; npm run build        # static export — may need TWO passes (see skills/qa-build.md)
cd apps/web ; npm run type-check

# Supabase
supabase start
supabase migration up              # local
supabase db push                   # cloud (requires linked project)
supabase gen types typescript --local | Out-File -FilePath apps/web/src/types/supabase.ts -Encoding UTF8

# Lambda deploy (from repo root)
python scripts/deploy-lambdas.py api
python scripts/deploy-lambdas.py events-scraper
python scripts/deploy-lambdas.py image-gen        # large package — uses S3
python scripts/deploy-lambdas.py content-generator

# Terraform — ⚠️ MUST use default profile
cd infra/terraform
$env:AWS_PROFILE="default"        # required — novakidlife profile lacks state permissions
terraform plan -out=tfplan
terraform apply tfplan             # always review plan first
```

---

## Critical Conventions

### Frontend
- Named exports only (except `page.tsx` / `layout.tsx`)
- `'use client'` only when genuinely needed
- All API fetches use `AbortSignal.timeout(8000)`
- `generateStaticParams` fallback: `[{ slug: '_placeholder' }]` — NOT `[]` (Next.js 15 rejects empty arrays)
- Build may need TWO passes — see `skills/qa-build.md` before every build

### Python / Lambda
- Entry point always `handler.py`
- All handlers call `_load_secrets_from_ssm()` at module init
- SSM prefix: `/novakidlife/`
- Tests: pytest · Linting: ruff

### Terraform
- Always `$env:AWS_PROFILE="default"` before any terraform command
- Never `apply` without reviewing `plan` first
- `social-poster` Lambda removed from Terraform (code preserved in `services/social-poster/`)

### Git
- Branch: `main` · Prefixes: `feat:` `fix:` `infra:` `chore:`

---

## Worktrees

| Worktree | Branch | Purpose |
|----------|--------|---------|
| `nova-kid-life` | `main` | Production + hotfixes |
| `nova-kid-life-content` | `feature-content` | Blog, copy, SEO |
| `nova-kid-life-events` | `feature-events` | Scraper, image pipeline |
| `nova-kid-life-infra` | `feature-infra` | Terraform, Lambda, CI/CD |

Never commit to `main` from a feature worktree. Merge explicitly with `--no-ff`.

---

## Skills Library

All operational runbooks in `/skills/`. Read the relevant skill before starting any major task.

**Key skills:**
- `qa-build.md` — ⭐ run before every `npm run build`
- `deploy-frontend.md` — S3 deploy + CloudFront invalidation
- `deploy-api.md` — Lambda package + publish
- `scraper-add-source.md` — adding new Tier 2 sources
- `generate-image.md` — full image pipeline SOP
- `geo-llm-optimizer.md` — LLM/AI citation optimization (highest priority SEO)
- `next-15-patterns.md` — Next.js 15 static export gotchas
- `autonomous-agents.md` — autonomous operation architecture

Full skill index in `skills/` directory.

---

## Reference Docs

- `docs/system-map.md` — complete bird's-eye system view
- `DESIGN_SYSTEM.md` — all visual/UI design tokens and rules
- `config/sources.json` — all Tier 2 scrape sources
- `services/image-gen/prompts.py` — all image prompt libraries