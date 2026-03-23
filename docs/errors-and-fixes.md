# Errors & Fixes — NovaKidLife

Running log of bugs encountered and how they were resolved.
Add entries in reverse-chronological order (newest at top).

Format:
```
## YYYY-MM-DD — Short description
**Session:** N
**Error:** What happened
**Root cause:** Why it happened
**Fix:** What resolved it
**Prevention:** How to avoid it next time
```

---

## 2026-03-23 — blog_posts ON CONFLICT fails — 42P10 no unique constraint
**Session:** 18
**Error:** Content generator Lambda returned `42P10 — there is no unique or exclusion constraint matching the ON CONFLICT specification`
**Root cause:** `blog_posts` table had a functional unique index using `COALESCE(area, 'nova')`. PostgreSQL `ON CONFLICT` can only target plain unique constraints or plain expression indexes — not functional indexes that call scalar functions.
**Fix:** Migration `20260323000001_fix_blog_posts_unique_constraint.sql` — dropped functional index, added `ALTER TABLE blog_posts ADD CONSTRAINT blog_posts_type_area_date_key UNIQUE (post_type, area, date_range_start)`. Applied via `supabase db push`.
**Prevention:** Use plain `UNIQUE` constraints for `ON CONFLICT` targets. Only use functional indexes for read-query optimization, not upserts.

---

## 2026-03-23 — Content generator trigger payload — "Unknown trigger: manual"
**Session:** 18
**Error:** Lambda invocation returned `{"error": "Unknown trigger: manual"}`
**Root cause:** Sent `{"trigger": "manual", "post_type": "week_ahead"}`. The handler validates `trigger` and only accepts `"weekend"` or `"week_ahead"`.
**Fix:** Changed payload to `{"trigger": "week_ahead"}`.
**Prevention:** Check handler.py for valid trigger values before invoking manually. Valid values: `weekend`, `week_ahead`.

---

## 2026-03-23 — Deploy Frontend fails — npm ci missing package from lock file
**Session:** 18
**Error:** GitHub Actions `npm ci` step failed: `Missing: @novakidlife/content-generator@0.1.0 from lock file`
**Root cause:** `package.json` workspaces array included the content-generator package after it was added, but `npm install` was never re-run locally. `package-lock.json` didn't have the workspace entry. `npm ci` (used in CI) fails hard on any lock file discrepancy.
**Fix:** Ran `npm install` locally, committed updated `package-lock.json`.
**Prevention:** Always run `npm install` and commit `package-lock.json` after adding workspace packages to root `package.json`.

---

## 2026-03-23 — image-gen Lambda exceeds 250MB unzipped limit
**Session:** 18
**Error:** Lambda deploy failed: `RequestEntityTooLargeException` (zip >70MB), then on S3 path: unzipped size 262MB+ exceeds Lambda's 250MB hard limit.
**Root cause:** `google-cloud-aiplatform` is a large dependency. Even with manylinux wheels and source stripping, the unzipped package exceeds Lambda's hard 250MB limit.
**Fix:** Excluded image-gen from CI/CD matrix entirely. Deploy manually only: `python scripts/deploy-lambdas.py image-gen`.
**Prevention:** image-gen MUST always be deployed via the manual script, not GitHub Actions. This is documented in `deploy-api.yml` comments and CLAUDE.md.

---

## 2026-03-23 — Terraform workflow "workflow file issue" — 0s failure
**Session:** 18
**Error:** Terraform GitHub Actions workflow failed instantly with "This run likely failed because of a workflow file issue" — 0 seconds, no steps ran.
**Root cause:** `terraform.yml` had an `env:` block with all lines commented out. YAML parsed this as `env: null`, which GitHub Actions rejected at parse time before any steps executed.
**Fix:** Removed the empty `env:` block entirely. Moved the comment to the relevant step.
**Prevention:** YAML blocks with no content (only comments) become `null`. Remove empty YAML blocks rather than commenting out all their contents.

---

## 2026-03-23 — GitHub Actions failing: aws-region secret not set
**Session:** 18
**Error:** All 3 deploy workflows failed at "Configure AWS credentials" step: `Input required and not supplied: aws-region`
**Root cause:** Workflows used `aws-region: ${{ secrets.AWS_REGION }}` but `AWS_REGION` was never added to the GitHub repository secrets. The other two AWS secrets were set; this one was missed.
**Fix:** Hardcoded `aws-region: us-east-1` in all 3 workflows. It's not sensitive config — the region is visible in all resource ARNs.
**Prevention:** When `AWS_REGION` is constant (not multi-region), hardcode it rather than using a secret.

---

## 2026-03-13 — bash script failed on Windows (WSL not configured)
**Session:** 1
**Error:** `bash apps/web/scritps/download-fonts.sh` → `WSL (10 - Relay) ERROR: CreateProcessCommon:800: execvpe(/bin/bash) failed`
**Root cause:** (1) Typo in path (`scritps` → `scripts`). (2) WSL is installed but misconfigured — `/bin/bash` unavailable inside WSL relay.
**Fix:** Replaced bash script with `apps/web/scripts/download-fonts.mjs` (Node.js, cross-platform). Run with: `node apps/web/scripts/download-fonts.mjs` from repo root.
**Prevention:** Prefer Node.js scripts for cross-platform dev tooling in this project. Save bash scripts for CI/CD only (Linux runners).

---

## 2026-03-19 — CORS 400 errors for non-www origin
**Session:** 15
**Error:** `https://novakidlife.com` (non-www) got CORS errors; `www.novakidlife.com` worked fine.
**Root cause:** `router.py` had a hardcoded `_CORS_HEADERS` dict with `Access-Control-Allow-Origin: https://www.novakidlife.com`. The non-www origin was never reflected.
**Fix:** Replaced with `_cors_headers(origin)` function that reflects the request origin if it's in `_ALLOWED_ORIGINS = {"https://novakidlife.com", "https://www.novakidlife.com"}`. All route handlers updated to extract `origin = event.get("_origin")` and pass to every `ok()`/`error()` call.
**Prevention:** Always use dynamic origin reflection for multi-domain CORS. Never hardcode a single origin.

---

## 2026-03-19 — Supabase upsert 400 — slug NOT NULL violation
**Session:** 15
**Error:** Every event upsert to Supabase returned 400 with `null value in column slug violates not-null constraint`.
**Root cause:** The `events` table has `slug NOT NULL UNIQUE` with no DB default. `image-gen/handler.py` was upserting events without a slug field — the scraper passes `source_url` but the DB requires a slug.
**Fix:** Added `_make_slug(title, source_url)` — generates `{title-slug}-{md5(source_url)[:6]}` for deterministic, unique slugs. Added `"slug": event.get("slug") or _make_slug(title, source_url)` to the upsert row.
**Prevention:** When adding NOT NULL columns with no default, update all insert paths immediately and add a test.

---

## 2026-03-19 — Supabase PATCH 400 — non-existent image_lqip column
**Session:** 15
**Error:** Image gen PATCH to Supabase returned 400: `column "image_lqip" of relation "events" does not exist`.
**Root cause:** `db_payload` in `image-gen/handler.py` included `"image_lqip": processed.lqip` but the DB schema only has `image_blurhash`. LQIP is stored as a data URL in `processor.py` but never added as a DB column.
**Fix:** Removed `image_lqip` from `db_payload`. LQIP is computed client-side from `image_blurhash` (the blurhash string), or embedded in the HTML at build time.
**Prevention:** Keep DB column list in CLAUDE.md and cross-check against code before inserting/patching.

---

## 2026-03-19 — Silent Lambda failures — SQS messages deleted on error
**Session:** 15
**Error:** DLQ at 0 messages but only 65 events in DB despite 440 messages consumed from queue.
**Root cause:** `process_event()` in `image-gen/handler.py` wraps the entire pipeline in `try/except` and returns `{"status": "error"}`. Lambda returns HTTP 200 → SQS treats as success → deletes message. Events fail silently with no retry.
**Fix (partial):** Added `resp.text` logging on 400 upserts so failures appear in CloudWatch. Full fix (re-raising exceptions) deferred.
**Prevention:** Lambda SQS handlers should re-raise exceptions after logging so SQS retries and eventually DLQs. Return 200 only on genuine success.

---

## 2026-03-19 — AWS CLI path mangling in Git Bash (Windows)
**Session:** 15
**Error:** `aws logs filter-log-events --log-group-name /aws/lambda/...` → `parameter validation failed: Invalid type for parameter logGroupName`.
**Root cause:** Git Bash (MSYS2) converts paths starting with `/` to Windows paths. `/aws/lambda/novakidlife-prod-api` became `C:/Program Files/Git/aws/lambda/...`.
**Fix:** Prefix command with `MSYS_NO_PATHCONV=1` to disable path conversion.
**Prevention:** Always use `MSYS_NO_PATHCONV=1` with AWS CLI commands that take ARN/path-style parameters in Git Bash.

---

## 2026-03-19 — Lambda invoke base64 in Git Bash
**Session:** 15
**Error:** `aws lambda invoke --payload '{"key":"val"}'` → `Invalid base64` error in Git Bash.
**Root cause:** Git Bash doesn't base64-encode the payload; AWS CLI v2 requires base64 on non-Linux shells.
**Fix:** Used Python subprocess: `base64.b64encode(json.dumps(payload).encode()).decode()` to generate the encoded payload string before passing to AWS CLI.
**Prevention:** Use PowerShell or Python when invoking Lambdas programmatically on Windows.

---

## 2026-03-18 — birthday_freebies import error in scraper
**Session:** 15
**Error:** Scraper Lambda crashed with `ImportError: cannot import name 'BirthdayFreebiesScraper'`.
**Root cause:** `config/sources.json` had a `birthday-freebies` entry with `"tier": "tier3"` but the corresponding `scrapers/tier3/birthday_freebies.py` was never written.
**Fix:** Set `"enabled": false` in sources.json for the `birthday-freebies` entry.
**Prevention:** Don't add a source to sources.json until its scraper file exists.

---

## 2026-03-18 — KrazyCouponLady 404s
**Session:** 15
**Error:** KrazyCouponLady scraper returned 404 for all URLs.
**Root cause:** URL paths changed: `/deals/restaurants/` and `/deals/freebies/` no longer exist on the site.
**Fix:** Updated `_URLS` in `tier3/krazy_coupon_lady.py` to current working paths: `/deals/food`, `/deals/freebies-and-samples`, `/deals`.
**Prevention:** Mark Tier 3 scrapers for quarterly URL validation.

---

## 2026-03-18 — Terraform `terraform.tfvars` not in S3 backend
**Session:** 12
**Error:** `terraform plan` failed: ACM cert ARN not found.
**Root cause:** `terraform.tfvars` with `web_acm_certificate_arn` was not committed (gitignored) and not present in CI.
**Fix:** Added `terraform.tfvars` to the repo (ARN is not a secret — it's a public certificate identifier).
**Prevention:** `terraform.tfvars` with non-secret values should be committed. Secrets belong in SSM, not tfvars.

---

<!-- Add new entries above this line -->
