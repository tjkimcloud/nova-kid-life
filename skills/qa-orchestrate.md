# Skill: QA Orchestration — Architecture, Gaps & Runbook

**Purpose:** Define the full QA orchestration model for NovaKidLife — how the QA lead
runs, what subagents do, what the known gaps are, and how each is mitigated.

Read this before building or modifying the QA pipeline.

---

## Architecture Overview

```
[Trigger: daily cron OR manual]
         │
         ▼
  QA Lead (Claude / Node runner)
  └─ runs qa-site.js --fast
  └─ categorizes failures
  └─ spawns subagents in parallel
         │
    ┌────┼─────────────────────────────┐
    ▼    ▼                             ▼
Frontend  Data / DB              API / Lambda
Agent     Agent                  Agent
    │    │                             │
    └────┴─────────────────────────────┘
         │  all subagents commit to feature branches
         ▼
  QA Lead re-runs --fast
  └─ all green → merge branches → deploy triggers
  └─ still failing → open GH issue, alert human
```

**Subagent domains:**

| Agent | Owns | Can touch |
|-------|------|-----------|
| Frontend | Rendering bugs, UI regressions | `apps/web/src/**` |
| Data/DB | Bad HTML in descriptions, stale/past events, aggregator URLs | Supabase via API or migration |
| API/Lambda | HTTP errors, broken endpoints, malformed responses | `services/api/**`, Lambda deploy |

---

## Known Gaps & Mitigations

These are documented failures of the architecture as designed. Each has a required mitigation.

---

### GAP 1 — Visual content quality is invisible to qa-site.js

**What happened:** The `<p>` and `</p>` tags rendering as literal text on event detail pages
(e.g., `/events/tot-drop-in-sterling-community-center-8802a1/`) — the page returned HTTP 200,
had correct structure, and passed every existing check. The bug was only found by a human
looking at the page.

**Root cause:** qa-site.js checks HTTP status and the presence of high-level strings.
It never inspects rendered HTML for artifacts like literal `<p>`, `&lt;`, double-escaped
entities, or `\n` in visible text.

**Mitigation:** Add a `checkDescriptionQuality()` check to qa-site.js that:
1. Fetches 5 random event slugs from the API directly (`/events/{slug}`)
2. Looks at the `description` field for known artifact patterns:
   - Literal `<p>` or `</p>` or `<br>` as text content (not in HTML context)
   - `&lt;p&gt;` (double-escaped)
   - Trailing `\n` or `\\n`
   - Empty description (`""` or `null`)
3. Flags as warning (not failure) since descriptions are DB content, not frontend

**Status:** Not yet implemented. Add to scripts/qa-site.js.

---

### GAP 2 — Blog pages are completely absent from QA

**What's missing:** `/blog` listing and `/blog/[slug]` pages are not checked at all.
No HTTP check, no content check, no image check.

**Risk:** A broken blog deploy (bad markdown render, 404 on slug, missing OG image)
goes undetected indefinitely.

**Mitigation:** Add `checkBlogPages()` to qa-site.js:
1. Fetch `/blog` — expect HTTP 200, contains "blog" or post titles
2. Fetch `/api/blog?limit=5` (or the blog API endpoint) — get 3 slugs
3. Hit `/blog/{slug}` for each — expect 200 and no "Page not found"
4. Check that rendered HTML does NOT contain literal `<p>` or `</p>` (same as GAP 1)

**Status:** Not yet implemented.

---

### GAP 3 — No concurrency lock on the orchestrator

**The problem:** GitHub Actions cron fires daily. If the previous run is still in
progress (slow fix, slow build), a second run starts simultaneously. Both find the
same failures. Both spawn agents. Both agents write conflicting changes to the same
files. Git merge conflict or corrupted state.

**Mitigation:**
- Orchestrator writes a lock file to S3 (`qa-state/lock.json`) at start
- Checks for lock before proceeding — exits if lock is < 30 min old
- Deletes lock on completion (success or failure)
- GitHub Actions: use `concurrency: group: qa-orchestrator` with `cancel-in-progress: false`
  so a new run waits rather than starts

**Status:** Not yet implemented. Required before enabling cron.

---

### GAP 4 — Auto-fixes commit directly to main → instant production deploy

**The problem:** `deploy-frontend.yml` triggers on every push to `main` that touches
`apps/web/**`. An automated fix commit = immediate production deploy with no review.
If the subagent's fix introduces a new bug, it's live within ~8 minutes.

**Mitigation:**
- Subagents commit to short-lived `fix/qa-{timestamp}` branches
- Orchestrator opens a PR, runs type-check + build in CI
- Only merges to main if CI passes (Lighthouse 90+, type-check clean, build succeeds)
- For data-only fixes (no frontend code change): safe to apply directly
- For Lambda fixes: require manual review before `python scripts/deploy-lambdas.py`

**Status:** Not yet implemented. Critical safety requirement.

---

### GAP 5 — Two-pass build requirement breaks automated builds

**What's documented in qa-build.md:** `npm run build` must be run TWICE. First pass
fails on Pages Router chunk resolution. Second pass succeeds. An automated runner
that runs it once will always fail and think the build is broken.

**Mitigation:** Any script or GH Actions step that runs `npm run build` must be:
```bash
cd apps/web && npm run build || npm run build
```
The `||` means "if first fails, run again." GitHub Actions already does this in
`deploy-frontend.yml` — but a new QA automation step must replicate it.

**Status:** Documented. Must be applied to any new automation that builds.

---

### GAP 6 — dangerouslySetInnerHTML now renders DB content without sanitization

**What changed (2026-04-07):** `EventDetailClient.tsx` now uses `dangerouslySetInnerHTML`
to render `event.description`. This is correct — descriptions contain HTML from the scraper.
But it opens an XSS surface if the scraper or AI ever emits malicious HTML.

**Current trust model:** Descriptions come from:
- AI-generated content (gpt-4o-mini) — safe
- Scraped venue sites (via AI extraction) — conditionally safe
- Direct HTML parsing from source pages — risky if source is compromised

**Mitigation:** Add a description sanitizer in the API (`services/api/models.py`)
before the field is returned. Allow: `<p>`, `<br>`, `<strong>`, `<em>`, `<ul>`, `<li>`, `<a href>`.
Strip: `<script>`, `<iframe>`, `on*` attributes, `javascript:` hrefs.
Use `bleach` (Python) or equivalent. This keeps the XSS surface in one place (the API)
rather than in every consumer.

**Status:** Not yet implemented. Medium priority — low real-world risk today, but correct
architecture requires it.

---

### GAP 7 — No check that the scraper is actually producing new events

**The problem:** The scraper runs daily at 6am. If it silently produces 0 new events
(no error, just nothing scraped), QA passes because old events still exist in the DB.
The site looks fine but is going stale.

**Mitigation:** Add `checkScraperFreshness()` to qa-site.js:
1. Hit `{API}/events?section=main&limit=5&sort=created_at_desc` (or similar)
2. Check that the most recently created event is < 48 hours old
3. If newest event is > 48h old → warning (scraper may have stopped)
4. If newest event is > 96h old → failure

**Status:** Requires API to support `sort=created_at` param — verify first.

---

### GAP 8 — No image validation

**The problem:** qa-site.js never fetches image URLs. An event card with a broken
image (S3 key deleted, wrong path, CloudFront 403) passes QA. This is visible to
every user viewing that event.

**Mitigation:** In the existing slug spot-check, also:
1. Read `image_url` from the API response
2. HEAD request to the image URL — expect 200
3. Sample 5 events — flag if any image 404s

**Status:** Not yet implemented. Add to `checkEventSlugs()` spot-check.

---

### GAP 9 — No SEO/metadata validation on production

**The problem:** Lighthouse only runs on PRs against a local build. Production could
have broken OG tags, missing canonical URLs, or incorrect JSON-LD — none of which
Lighthouse would catch post-deploy.

**Mitigation:** Add `checkSeoMetadata()` to qa-site.js:
1. Fetch homepage HTML
2. Assert: `<meta property="og:title"` present
3. Assert: `<meta property="og:image"` present and non-empty
4. Assert: `<link rel="canonical"` present
5. Assert: `<script type="application/ld+json"` present (JSON-LD)
6. Fetch one event detail page — assert same fields + `EventSchema` in JSON-LD

**Status:** Not yet implemented.

---

### GAP 10 — No API latency threshold

**The problem:** qa-site.js checks that the API responds, not how fast. A degraded
Lambda that responds in 8s (vs. normal 300ms) passes QA but causes timeouts on the
frontend (AbortSignal.timeout(8000) — barely squeaks through).

**Mitigation:** Record response time in each `fetch()` call. Flag any API endpoint
that takes > 3000ms as a warning, > 6000ms as a failure.

**Status:** Partially implementable today — `fetch()` already uses `Date.now()`.

---

### GAP 11 — Python Lambda tests only run on PRs, not daily

**The problem:** `test.yml` runs pytest for all 5 services, but only on PRs. If a
Lambda breaks due to a dependency update, an SSM config change, or a DB schema drift,
no test will catch it until the next PR is opened.

**Mitigation:** Add a `test-lambdas` job to the daily QA cron that runs pytest for
the API and scraper services (the most critical ones). Image-gen and social-poster
can remain PR-only.

**Status:** Not yet implemented.

---

### GAP 12 — No escalation path from subagent to human

**The problem:** Subagents are spawned to fix issues. If the subagent cannot diagnose
or safely fix the issue (e.g., a Lambda memory limit, an SSM secret rotation, a
DB migration required), it has no formal way to escalate. The orchestrator sees no
failure and moves on.

**Mitigation:**
- Subagents must produce a structured JSON result:
  ```json
  { "status": "fixed|escalated|skipped", "description": "...", "pr_url": null }
  ```
- Orchestrator collects all results. Any `"escalated"` → open a GH issue with
  `qa-escalation` label and tag human reviewer.
- GH issue template lives at `.github/ISSUE_TEMPLATE/qa-escalation.md`

**Status:** Not yet implemented. Required before enabling autonomous mode.

---

### GAP 13 — No HTTPS / www redirect check

**The problem:** `http://novakidlife.com` and `www.novakidlife.com` should both
redirect to `https://novakidlife.com`. CloudFront handles this — but if the
distribution is ever misconfigured, the redirect breaks silently.

**Mitigation:** Add to `checkStaticPages()`:
```js
const r = await fetch('http://novakidlife.com', { redirect: 'manual' })
assert r.status === 301 or 302, location starts with 'https://novakidlife.com'
```
Note: Node's built-in `http.get` follows redirects by default — need to set
`maxRedirects: 0` or use a raw socket check.

**Status:** Not yet implemented.

---

## Priority Order for Implementation

| Priority | Gap | Effort | Risk if ignored |
|----------|-----|--------|----------------|
| P0 | GAP 3 — concurrency lock | Low | Data corruption from parallel agents |
| P0 | GAP 4 — fixes go to branches, not main | Low | Bad auto-fix goes live immediately |
| P1 | GAP 1 — description HTML artifact check | Low | Visible rendering bugs undetected |
| P1 | GAP 5 — two-pass build in automation | Low | Automation always fails on build |
| P1 | GAP 2 — blog page QA | Low | Blog breakages invisible |
| P2 | GAP 6 — dangerouslySetInnerHTML sanitizer | Medium | XSS surface (low real risk today) |
| P2 | GAP 7 — scraper freshness check | Low | Stale site undetected |
| P2 | GAP 8 — image 404 check | Low | Broken images undetected |
| P2 | GAP 12 — escalation path | Medium | Agent silently gives up |
| P3 | GAP 9 — SEO metadata check | Low | OG/canonical breakage undetected |
| P3 | GAP 10 — API latency threshold | Low | Slow API undetected |
| P3 | GAP 11 — daily Lambda tests | Low | Lambda regressions undetected |
| P3 | GAP 13 — HTTPS redirect check | Low | CloudFront misconfig undetected |

---

## Subagent Contracts

Each subagent spawned by the orchestrator must:

1. Receive a structured failure report (JSON) from the orchestrator
2. Read only what it needs — do not re-run full QA
3. Make minimal targeted fixes — do not refactor surrounding code
4. Commit to a branch named `fix/qa-{category}-{yyyymmdd}`
5. Return a structured result JSON (status, description, branch name)
6. Never push directly to main
7. Never run `terraform apply` or drop DB tables
8. If it cannot fix something with high confidence, set status=escalated

---

## Running QA Manually

```powershell
# Full audit (samples 50 event slugs) — ~2-3 min
node scripts/qa-site.js

# Fast mode (skip slug checks) — ~15s
node scripts/qa-site.js --fast

# Sample fewer slugs
node scripts/qa-site.js --sample 10
```

Exit code 0 = all checks passed. Exit code 1 = one or more failures.

---

## Files in this System

| File | Purpose |
|------|---------|
| `scripts/qa-site.js` | Live-site QA runner |
| `scripts/qa-orchestrate.js` | Orchestrator (to be built) |
| `.github/workflows/qa-scheduled.yml` | Daily cron trigger (to be built) |
| `skills/qa-build.md` | Pre-build checklist (read before building) |
| `skills/qa-orchestrate.md` | This file — architecture + gaps |
