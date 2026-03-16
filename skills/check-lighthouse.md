# Skill: Lighthouse CI

**Purpose:** Run Lighthouse performance, SEO, and accessibility audits on the frontend.

## Targets
- Performance: ≥ 90
- Accessibility: ≥ 95
- Best Practices: ≥ 90
- SEO: ≥ 95

## Local Audit (single page)

```bash
# Install once
npm install -g @lhci/cli lighthouse

# Build the site first
cd apps/web && npm run build

# Serve the static export
npx serve out -p 3000 &
SERVER_PID=$!

# Run Lighthouse
lighthouse http://localhost:3000 \
  --output=html \
  --output-path=/tmp/lighthouse-report.html \
  --chrome-flags="--headless --no-sandbox" \
  --only-categories=performance,accessibility,best-practices,seo

kill $SERVER_PID
open /tmp/lighthouse-report.html  # macOS; use xdg-open on Linux
```

## LHCI Collect (full CI run)

```bash
# From repo root
npx lhci collect \
  --url=http://localhost:3000 \
  --url=http://localhost:3000/events \
  --settings.chromeFlags="--headless --no-sandbox"

npx lhci assert --config=.lighthouserc.js
```

## `.lighthouserc.js` (create at repo root)

```js
module.exports = {
  ci: {
    collect: {
      staticDistDir: './apps/web/out',
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.95 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['warn', { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
}
```

## Common Failures and Fixes

| Audit Failure | Fix |
|---------------|-----|
| LCP > 2.5s | Preload hero image, check image sizes |
| CLS > 0.1 | Add explicit `width`/`height` to images |
| Missing alt text | Add `alt` to all `<img>` tags |
| Missing meta description | Set in `layout.tsx` metadata |
| Not using HTTPS | Always test against `https://` in CI |
| Render-blocking resources | Move scripts to `defer`, fonts to `swap` |

## Check Core Web Vitals (Production)

```bash
# Use PageSpeed Insights API
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://novakidlife.com&strategy=mobile" \
  | jq '.lighthouseResult.categories | {perf: .performance.score, a11y: .accessibility.score, seo: .seo.score}'
```

## GitHub Actions
See `.github/workflows/lighthouse.yml` — runs on every PR against `main`.
