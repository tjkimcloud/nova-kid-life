# Architectural Decision Records — NovaKidLife

Format: ADR-NNN | Title | Status | Date

---

## ADR-001 | S3 + CloudFront over Vercel
**Status:** Adopted | **Date:** 2026-03-13

### Context
The frontend is a Next.js 14 app. Vercel is the default deployment target for Next.js, offering zero-config deploys, edge functions, and ISR. AWS S3 + CloudFront is the alternative.

### Decision
Deploy as a static export to S3 + CloudFront.

### Rationale
- **Portfolio:** Project is explicitly an AWS portfolio piece — all infrastructure should live in AWS
- **Cost:** Vercel Pro is ~$20/mo; S3 + CloudFront for a small site is <$2/mo at this traffic level
- **Control:** Full control over cache headers, CDN behavior, and invalidation strategy
- **Lock-in:** Avoids Vercel-specific features (ISR, Edge Functions) that don't translate to other platforms
- **SSR not needed:** Events data changes ~daily; static export with daily rebuilds is sufficient

### Trade-offs Accepted
- No ISR (Incremental Static Regeneration) — full rebuild on content changes
- No Vercel preview deployments — must configure manually in GitHub Actions
- More infrastructure to manage (2 Terraform resources vs. zero)

---

## ADR-002 | SQS for Async Pipeline Decoupling
**Status:** Adopted | **Date:** 2026-03-13

### Context
The content pipeline (scrape → AI enrich → image gen → social post) involves multiple steps, each potentially slow or failure-prone. Options: direct Lambda chaining, Step Functions, or SQS queues.

### Decision
Use SQS queues between pipeline stages with DLQs for failed messages.

### Rationale
- **Decoupling:** Each stage scales independently; image-gen Lambda can lag without blocking scraper
- **Retry logic:** SQS provides built-in retry with configurable visibility timeout — no custom retry code
- **DLQ:** Failed events park in DLQ for inspection, not silently dropped
- **Cost:** SQS is essentially free at this volume (<$1/month for millions of messages)
- **Simplicity:** Step Functions adds visual appeal but significant complexity overhead for a solo project

### Trade-offs Accepted
- No native ordering guarantees (Standard Queue) — acceptable since events are independent
- Debugging pipeline failures requires checking SQS + CloudWatch together

---

## ADR-003 | Pluggable ImageGenService (Imagen 3 + DALL-E 3)
**Status:** Adopted | **Date:** 2026-03-13

### Context
AI image generation market is rapidly evolving. Locking into one provider risks quality regression, pricing changes, or deprecation. Imagen 3 and DALL-E 3 are current leaders.

### Decision
Implement an adapter pattern: Imagen 3 as primary, DALL-E 3 as automatic fallback, with a shared interface so additional providers can be added without changing calling code.

### Rationale
- **Vendor flexibility:** Can switch primary provider by changing one config value
- **Resilience:** Automatic fallback means no failed images if Imagen 3 has an outage
- **Cost optimization:** Can A/B test providers on image quality vs. cost
- **Future-proofing:** Stable2, Midjourney API, or other providers can be added as adapters

### Interface Contract
```python
class ImageGenAdapter(Protocol):
    def generate(self, prompt: str) -> bytes: ...
```

---

## ADR-004 | Supabase over DynamoDB
**Status:** Adopted | **Date:** 2026-03-13

### Context
The primary database could be DynamoDB (native AWS, NoSQL, serverless) or Supabase (managed PostgreSQL, SQL, built-in auth + realtime).

### Decision
Use Supabase (PostgreSQL).

### Rationale
- **Query flexibility:** Event discovery requires complex filtering (date range, location radius, age range, tags). SQL is dramatically easier than DynamoDB filter expressions
- **pgvector:** Semantic search ("outdoor activities for toddlers") requires vector similarity — pgvector is a first-class Supabase extension; DynamoDB has no native vector search
- **Managed auth:** Supabase Auth handles newsletter subscription auth if added later
- **Development speed:** Supabase dashboard, auto-generated API, and SQL editor are far faster for a solo developer than DynamoDB + PartiQL
- **Cost:** Supabase free tier handles early-stage traffic; Pro is $25/mo when needed

### Trade-offs Accepted
- Not "pure AWS" — Supabase is an external service
- PostgreSQL connection pooling must be managed at Lambda cold-start (use pgBouncer or Supabase connection pooler)

---

## ADR-005 | Next.js Static Export (No SSR/ISR)
**Status:** Adopted | **Date:** 2026-03-13

### Context
Next.js supports SSR, ISR, and static export. Event data changes daily. Static export generates HTML at build time.

### Decision
Use `output: 'export'` — full static export, rebuilt daily via CI/CD.

### Rationale
- **Performance:** Pre-rendered HTML = fastest possible TTFB from CloudFront edge
- **Cost:** No server compute — just S3 + CloudFront
- **Simplicity:** No Lambda@Edge, no Node.js server, no cold starts for page renders
- **SEO:** Static HTML is the gold standard for search engine crawlability
- **Rebuild cadence:** Daily scrape → daily rebuild → content freshness is acceptable (events don't change hour-to-hour)

### Trade-offs Accepted
- User-submitted content or personalization would require rethinking this
- Search/filter is handled client-side or via API calls (not ISR pages)

---

## ADR-008 | Local Supabase (Docker) for Development
**Status:** Adopted | **Date:** 2026-03-13

### Context
Supabase free tier is limited to 2 active projects. Existing portfolio projects occupy both slots. Options were: multiple email accounts, Neon.tech, or local Supabase via Docker.

### Decision
Run Supabase locally via Docker + Supabase CLI for all development. Migrate to a paid cloud Supabase project at launch (Session 12).

### Rationale
- **Standard workflow:** Local-first is Supabase's own recommended dev pattern
- **Free and unlimited:** No tier limits, no cost during development
- **Same tooling:** Migrations written locally apply identically to cloud — `supabase db push` at launch
- **Docker already installed:** No additional tooling cost
- **Offline capable:** Development works without internet

### Trade-offs Accepted
- Must have Docker Desktop running during development
- Local Studio URL (localhost:54323) instead of cloud dashboard
- Cloud project + billing needed at launch (~$25/mo)

---

## ADR-006 | Python 3.12 for All Lambda Functions
**Status:** Adopted | **Date:** 2026-03-13

### Context
Lambda supports multiple runtimes: Node.js, Python, Go, Java, etc. The AI/ML ecosystem (OpenAI SDK, Google Vertex AI, BeautifulSoup, etc.) is Python-native.

### Decision
Python 3.12 for all Lambda functions.

### Rationale
- **Ecosystem:** Best AI/ML library support (openai, google-cloud-aiplatform, supabase-py)
- **Web scraping:** BeautifulSoup, httpx, Playwright all have excellent Python support
- **Team consistency:** One language across all backend services
- **AWS support:** Python 3.12 is a supported Lambda runtime with active maintenance

---

## ADR-007 | Terraform for Infrastructure as Code
**Status:** Adopted | **Date:** 2026-03-13

### Context
Infrastructure could be managed via AWS CDK (TypeScript), SAM, Pulumi, or Terraform.

### Decision
Terraform with S3 backend and DynamoDB state locking.

### Rationale
- **Portfolio:** Terraform is the industry-standard IaC tool; strongest resume signal
- **Multi-cloud:** Terraform manages both AWS and GCP (Vertex AI) resources in one tool
- **Ecosystem:** Largest provider ecosystem; excellent AWS provider coverage
- **State management:** S3 + DynamoDB locking is battle-tested for solo projects

### Trade-offs Accepted
- HCL syntax is less familiar than TypeScript (CDK)
- No native Lambda packaging — must zip manually (or use `archive_file` data source)
