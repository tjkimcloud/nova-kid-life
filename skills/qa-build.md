# Skill: QA + Build Validation

**Purpose:** Pre-build checklist for NovaKidLife. Run through this before every `npm run build`.

> For Next.js 15 gotchas, TypeScript patterns, and environment variable rules — see `next-15-patterns.md`.

---

## Run Order

```powershell
cd apps/web
npm run type-check   # TypeScript only — fast, fix errors here first
npm run build        # Full static export
```

Fix type errors before running build. They're the same errors, type-check is just faster.

**Build quirk:** Run `npm run build` TWICE without clearing `.next` between runs. The first pass fails on Pages Router chunk resolution. The second pass succeeds. **Never `rm -rf .next` before a build unless you plan to run twice.**

---

## Pre-Commit Checklist

Before every `git commit` that touches `apps/web/`:

### Required
- [ ] `npm run type-check` — zero errors
- [ ] `npm run build` — "Export successful", check output in `apps/web/out/`
- [ ] Every new `[param]` dynamic route has `generateStaticParams` + `dynamicParams = false`
- [ ] Every new `robots.ts` / `sitemap.ts` has `export const dynamic = 'force-static'`
- [ ] No `notFound()` inside catch blocks
- [ ] No interactive forms in server components
- [ ] No `async headers()` in `next.config.js`

### SEO (for pages touching content)
- [ ] Title: 50–60 chars, includes geographic signal
- [ ] Meta description: 140–155 chars
- [ ] One H1 per page
- [ ] Canonical URL set in metadata
- [ ] JSON-LD schema appropriate for page type
- [ ] New page added to `sitemap.ts`
- [ ] New page linked from at least one other page (internal link)

### Components
- [ ] `'use client'` on any component using hooks or browser APIs
- [ ] No `'use client'` on components that don't need it (adds JS bundle weight)
- [ ] All `<img>` tags have explicit `width` + `height` + `alt`
- [ ] New components exported as named exports (not default)

---

## Build Output Verification

After a successful `npm run build`, check `apps/web/out/`:

```powershell
ls apps/web/out/           # should have index.html, events/, pokemon/, about/, etc.
ls apps/web/out/events/    # should have index.html (listing page)
ls apps/web/out/about/     # should have index.html
```

Spot-check that key pages exist and aren't empty:
```powershell
(Get-Content apps/web/out/index.html).Length         # homepage — should be >10000 chars
(Get-Content apps/web/out/events/index.html).Length  # events listing
(Get-Content apps/web/out/about/index.html).Length   # about page
```

---

## Common Error: `Cannot find module './NNN.js'` on `/404` or `/500`

```
Error: Cannot find module './611.js'
Require stack: webpack-runtime.js → pages/_document.js
Export encountered an error on /_error: /404, exiting the build.
```

**Fix:** Run `npm run build` TWICE without clearing `.next`. First pass creates the chunk structure the second pass needs.

## Common Warning: "headers" with static export

```
⚠ Specified "headers" will not automatically work with "output: export"
```

Harmless and expected if `async headers()` is in `next.config.js`. Remove it — CloudFront handles headers.
