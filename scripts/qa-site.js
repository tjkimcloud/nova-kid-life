#!/usr/bin/env node
/**
 * qa-site.js — Automated site QA for novakidlife.com
 *
 * Checks:
 *  1. Homepage loads and has expected sections
 *  2. Events page loads and shows events
 *  3. Sitemap is valid and all slugs are accessible
 *  4. Event detail pages render actual event content (not "Page not found")
 *  5. API /events returns live data
 *  6. API /sitemap returns slugs
 *
 * Usage:
 *   node scripts/qa-site.js              # full audit
 *   node scripts/qa-site.js --fast       # homepage + API only (skips slug checks)
 *   node scripts/qa-site.js --sample 20  # check N random event slugs
 */

const https = require('https')
const http  = require('http')

const SITE = 'https://novakidlife.com'
const API  = 'https://api.novakidlife.com'
const FAST = process.argv.includes('--fast')
const SAMPLE_IDX = process.argv.indexOf('--sample')
const SAMPLE_N = SAMPLE_IDX !== -1 ? parseInt(process.argv[SAMPLE_IDX + 1] || '20', 10) : 50

// ── Helpers ───────────────────────────────────────────────────────────────────

function fetch(url, timeout = 12000) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http
    const req = lib.get(url, { headers: { 'User-Agent': 'NovaKidLife-QA/1.0' } }, (res) => {
      let body = ''
      res.on('data', d => body += d)
      res.on('end', () => resolve({ status: res.statusCode, body, headers: res.headers }))
    })
    req.on('error', reject)
    req.setTimeout(timeout, () => { req.destroy(); reject(new Error(`Timeout: ${url}`)) })
  })
}

let pass = 0, fail = 0, warn = 0
const failures = []
const timings  = {}

function ok(msg)      { pass++; console.log(`  ✅ ${msg}`) }
function bad(msg)     { fail++; failures.push(msg); console.log(`  ❌ ${msg}`) }
function warning(msg) { warn++; console.log(`  ⚠️  ${msg}`) }
function section(title) { console.log(`\n── ${title} ${'─'.repeat(Math.max(0, 60 - title.length))}`) }

// Timed fetch — records ms for latency checks
async function timedFetch(url, timeout = 12000) {
  const t0 = Date.now()
  const result = await fetch(url, timeout)
  timings[url] = Date.now() - t0
  return result
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

// ── Checks ────────────────────────────────────────────────────────────────────

async function checkHomepage() {
  section('Homepage')
  try {
    const { status, body } = await fetch(SITE)
    if (status !== 200) return bad(`Homepage HTTP ${status}`)
    ok(`Homepage HTTP 200`)

    const visible = stripScripts(body)
    const checks = [
      ['Hero heading',         'Find something'],
      ['Week section',         'Upcoming Events This Week'],
      ['Browse by interest',   'Browse by interest'],
      ['Newsletter section',   'Never Miss'],
    ]
    for (const [label, needle] of checks) {
      if (body.includes(needle)) ok(label)
      else bad(`${label} — expected text not found`)
    }
    if (visible.includes('Page not found')) bad(`Homepage shows "Page not found" in visible body`)
    else ok('No "Page not found" in visible homepage body')
  } catch (e) {
    bad(`Homepage fetch failed: ${e.message}`)
  }
}

async function checkEventsPage() {
  section('Events Page')
  try {
    const { status, body } = await fetch(`${SITE}/events`)
    if (status !== 200) return bad(`Events page HTTP ${status}`)
    ok(`Events page HTTP 200`)
    const visible = stripScripts(body)
    if (visible.includes('Page not found')) bad(`Events page shows "Page not found" in visible body`)
    else ok(`Events page has no "Page not found" in visible body`)
    if (body.includes('events') || body.includes('Events')) ok(`Events page contains events content`)
    else warning(`Events page may be empty`)
  } catch (e) {
    bad(`Events page fetch failed: ${e.message}`)
  }
}

async function checkApiEventRendering() {
  // The events page is client-rendered — the HTML only has a loading skeleton.
  // Verify that the API actually serves data that would populate the page.
  section('API → Events Page Rendering Check')
  const tests = [
    { label: 'Browse all events (/events)',         url: `${API}/events?section=main&limit=12&offset=0` },
    { label: 'Free this weekend (/events?free=true)', url: `${API}/events?section=main&is_free=true&limit=12&offset=0` },
    { label: 'Today filter (/events?date=today)',   url: (() => {
        const today = new Date().toISOString().split('T')[0]
        return `${API}/events?section=main&start_date=${today}&end_date=${today}&limit=12&offset=0`
      })() },
  ]
  for (const { label, url } of tests) {
    try {
      const { status, body } = await fetch(url)
      if (status !== 200) { bad(`${label} — API HTTP ${status}`); continue }
      const data = JSON.parse(body)
      if (data.total > 0) ok(`${label} — ${data.total} events available`)
      else warning(`${label} — 0 events (page would show empty state)`)
    } catch (e) {
      bad(`${label} — ${e.message}`)
    }
  }
}

async function checkApi() {
  section('API Health')
  try {
    // /events
    const { status, body } = await fetch(`${API}/events?limit=5&section=main`)
    if (status !== 200) return bad(`API /events HTTP ${status}`)
    const data = JSON.parse(body)
    const count = data.items?.length ?? 0
    if (count > 0) ok(`API /events returned ${count} events (total: ${data.total})`)
    else bad(`API /events returned 0 events`)

    // Check event has expected fields
    const ev = data.items?.[0]
    if (ev) {
      const fields = ['id', 'slug', 'title', 'start_at', 'location_name']
      const missing = fields.filter(f => !ev[f])
      if (missing.length) bad(`Event missing fields: ${missing.join(', ')}`)
      else ok(`Event shape has all required fields`)

      // Check registration_url not pointing to aggregator
      const AGGREGATORS = ['dullesmoms.com', 'patch.com', 'macaronikid.com', 'mommypoppins.com']
      const reg = ev.registration_url || ''
      if (reg && AGGREGATORS.some(a => reg.includes(a))) {
        warning(`Sample event registration_url still points to aggregator: ${reg}`)
      }
    }
  } catch (e) {
    bad(`API /events failed: ${e.message}`)
  }

  try {
    // /sitemap
    const { status, body } = await fetch(`${API}/sitemap`)
    if (status !== 200) return bad(`API /sitemap HTTP ${status}`)
    const data = JSON.parse(body)
    const slugs = data.main_events ?? data.main ?? []
    if (slugs.length > 0) ok(`API /sitemap returned ${slugs.length} event slugs`)
    else bad(`API /sitemap returned 0 slugs`)
    return slugs
  } catch (e) {
    bad(`API /sitemap failed: ${e.message}`)
    return []
  }
}

function stripScripts(html) {
  // Remove <script> tags so we only check visible body content
  return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
}

async function checkEventSlugs(slugs) {
  section(`Event Detail Pages (sampling ${SAMPLE_N} of ${slugs.length})`)
  if (slugs.length === 0) return warning('No slugs to check')

  const sample = shuffle([...slugs]).slice(0, SAMPLE_N)
  let hasContent = 0, missingContent = 0, errors = 0
  const brokenUrls = []

  await Promise.all(
    sample.map(async (item) => {
      const slug = typeof item === 'string' ? item : item.slug
      const url = `${SITE}/events/${slug}`
      try {
        const { status, body } = await fetch(url, 15000)
        if (status !== 200) {
          errors++
          bad(`HTTP ${status}: ${url}`)
          return
        }
        // Check visible body only (strip scripts — Next.js RSC payload includes
        // the _not-found component code as dead code on every page)
        const visible = stripScripts(body)
        // Event pages use client-side rendering: initial HTML has a skeleton
        // (animate-pulse). The API must serve the slug for full render.
        const hasSkeleton = visible.includes('animate-pulse')
        const hasPageNotFound = visible.includes('Page not found')
        if (hasPageNotFound) {
          missingContent++
          brokenUrls.push(url)
        } else if (hasSkeleton || visible.includes('EventDetailClient')) {
          hasContent++
        } else {
          missingContent++
          brokenUrls.push(url)
        }
      } catch (e) {
        errors++
        bad(`Fetch error ${slug}: ${e.message}`)
      }
    })
  )

  if (hasContent > 0) ok(`${hasContent}/${sample.length} event pages have correct skeleton HTML`)
  if (missingContent > 0) {
    bad(`${missingContent}/${sample.length} event pages missing content or showing "Page not found" in body`)
    brokenUrls.slice(0, 5).forEach(u => console.log(`     → ${u}`))
  }
  if (errors > 0) warning(`${errors}/${sample.length} event pages had fetch errors`)

  // Spot-check 3 slugs against the API to confirm data is actually there
  section('API spot-check for event data')
  const spot = shuffle([...slugs]).slice(0, 3)
  await Promise.all(spot.map(async (item) => {
    const slug = typeof item === 'string' ? item : item.slug
    try {
      const { status, body } = await fetch(`${API}/events/${slug}`, 10000)
      if (status !== 200) { bad(`API event ${slug} → HTTP ${status}`); return }
      const ev = JSON.parse(body)
      if (ev.title) ok(`API data for "${ev.title.slice(0, 40)}"`)
      else bad(`API event ${slug} missing title`)
      // Flag if registration_url is still an aggregator
      const AGGREGATORS = ['dullesmoms.com','patch.com','macaronikid.com','mommypoppins.com']
      const reg = ev.registration_url || ''
      if (reg && AGGREGATORS.some(a => reg.includes(a))) {
        warning(`registration_url is aggregator for ${slug}: ${reg.slice(0, 60)}`)
      }
    } catch (e) {
      bad(`API spot-check ${slug}: ${e.message}`)
    }
  }))
}

async function checkStaticPages() {
  section('Static Pages')
  const pages = [
    ['/about',          'About'],
    ['/pokemon',        ''],
    ['/privacy-policy', ''],
    ['/sitemap.xml',    '<urlset'],
    ['/robots.txt',     'User-Agent'],
  ]
  await Promise.all(pages.map(async ([path, needle]) => {
    try {
      const { status, body } = await fetch(`${SITE}${path}`)
      if (status !== 200) bad(`${path} HTTP ${status}`)
      else if (needle && !body.includes(needle)) warning(`${path} may be missing expected content`)
      else ok(`${path} HTTP 200`)
    } catch (e) {
      bad(`${path} failed: ${e.message}`)
    }
  }))
}

// ── Description quality (GAP 1) ───────────────────────────────────────────────
// Checks API description fields for known HTML artifacts that render as
// visible broken text (e.g. literal <p> tags, double-escaped entities).

// Artifacts checked in raw API string fields (descriptions are now rendered as HTML,
// so <p> tags are valid there — only flag things that break even in HTML rendering)
const API_ARTIFACTS = [
  { pattern: /&lt;p&gt;/,   label: 'double-escaped <p> — would show as literal text in HTML' },
  { pattern: /&lt;\/p&gt;/, label: 'double-escaped </p> — would show as literal text in HTML' },
  { pattern: /&amp;lt;/,    label: 'triple-escaped entity' },
]

// Artifacts checked in rendered static HTML source (server-rendered pages)
// These indicate a renderer bug where block elements got wrapped in <p> tags
const RENDER_ARTIFACTS = [
  { pattern: /<p>\s*<h[23]/i,  label: 'heading wrapped in <p> (renderer bug)' },
  { pattern: /<p>\s*<hr/i,     label: '<hr> wrapped in <p> (renderer bug)' },
  { pattern: /&lt;p&gt;/,      label: 'double-escaped <p> visible in page source' },
  { pattern: /&lt;\/p&gt;/,    label: 'double-escaped </p> visible in page source' },
]

async function checkDescriptionQuality() {
  section('Description HTML Quality (GAP 1)')
  try {
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=20&offset=0`)
    if (status !== 200) { bad(`API /events HTTP ${status} — skipping description check`); return }
    const data = JSON.parse(body)
    const items = data.items ?? []
    if (items.length === 0) { warning('No events returned — skipping description check'); return }

    let clean = 0, dirty = 0
    for (const ev of items) {
      const desc = ev.description ?? ''
      if (!desc) continue
      const hits = API_ARTIFACTS.filter(({ pattern }) => pattern.test(desc))
      if (hits.length) {
        dirty++
        bad(`"${ev.title?.slice(0, 40)}" — description contains ${hits.map(h => h.label).join(', ')}`)
      } else {
        clean++
      }
    }
    if (dirty === 0) ok(`All ${clean} sampled descriptions are artifact-free`)
  } catch (e) {
    bad(`Description quality check failed: ${e.message}`)
  }
}

// ── Blog pages (GAP 2) ────────────────────────────────────────────────────────

async function checkBlogPages() {
  section('Blog Pages (GAP 2)')
  try {
    const { status, body } = await timedFetch(`${SITE}/blog`)
    if (status !== 200) return bad(`/blog HTTP ${status}`)
    ok(`/blog HTTP 200`)
    const visible = stripScripts(body)
    if (visible.includes('Page not found')) bad('/blog shows "Page not found"')
    else ok('/blog has no "Page not found"')
  } catch (e) {
    bad(`/blog fetch failed: ${e.message}`)
    return
  }

  // Get a few blog slugs from the API
  try {
    const { status, body } = await timedFetch(`${API}/blog?limit=3`)
    if (status !== 200) { warning(`Blog API HTTP ${status} — skipping slug check`); return }
    const data = JSON.parse(body)
    const slugs = (data.items ?? []).map(p => p.slug).filter(Boolean)
    if (slugs.length === 0) { warning('No blog slugs returned from API'); return }

    await Promise.all(slugs.map(async (slug) => {
      try {
        const { status: s, body: b } = await timedFetch(`${SITE}/blog/${slug}`, 15000)
        if (s !== 200) { bad(`/blog/${slug} HTTP ${s}`); return }
        const visible = stripScripts(b)
        if (visible.includes('Page not found')) { bad(`/blog/${slug} shows "Page not found"`); return }
        // Check for renderer artifacts — block elements wrapped in <p>, double-escaped HTML
        const hits = RENDER_ARTIFACTS.filter(({ pattern }) => pattern.test(b))
        if (hits.length) bad(`/blog/${slug} — ${hits.map(h => h.label).join(', ')}`)
        else ok(`/blog/${slug} — clean`)
      } catch (e) {
        bad(`/blog/${slug} fetch failed: ${e.message}`)
      }
    }))
  } catch (e) {
    warning(`Blog slug check failed: ${e.message}`)
  }
}

// ── SEO metadata (GAP 9) ──────────────────────────────────────────────────────

async function checkSeoMetadata() {
  section('SEO Metadata (GAP 9)')
  const checks = [
    { url: SITE,            label: 'Homepage' },
    { url: `${SITE}/events`, label: 'Events page' },
  ]

  for (const { url, label } of checks) {
    try {
      const { status, body } = await timedFetch(url)
      if (status !== 200) { bad(`${label} HTTP ${status}`); continue }

      const seoChecks = [
        ['og:title',       /property="og:title"/],
        ['og:image',       /property="og:image"/],
        ['canonical',      /rel="canonical"/],
        ['meta description', /name="description"/],
      ]
      for (const [name, pattern] of seoChecks) {
        if (pattern.test(body)) ok(`${label} — ${name} present`)
        else bad(`${label} — missing ${name}`)
      }
    } catch (e) {
      bad(`${label} SEO check failed: ${e.message}`)
    }
  }
}

// ── Scraper freshness (GAP 7) ─────────────────────────────────────────────────

async function checkScraperFreshness() {
  section('Scraper Freshness (GAP 7)')
  try {
    // Use upcoming events sorted by start_at ascending — newest scraped should be in the future
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=50&offset=0`)
    if (status !== 200) { bad(`API /events HTTP ${status}`); return }
    const data = JSON.parse(body)
    const items = data.items ?? []
    if (items.length === 0) { bad('No events in feed — scraper may be down'); return }

    // Find the most recently starting event
    const now = Date.now()
    const futureEvents = items.filter(ev => new Date(ev.start_at).getTime() > now)
    if (futureEvents.length === 0) {
      bad('No future events in top 50 — all events are in the past, scraper may be stale')
      return
    }

    // Check: is there at least 1 event starting within the next 14 days?
    const twoWeeks = now + 14 * 24 * 60 * 60 * 1000
    const upcoming = futureEvents.filter(ev => new Date(ev.start_at).getTime() < twoWeeks)
    if (upcoming.length > 0) ok(`${upcoming.length} events in the next 14 days — scraper active`)
    else warning('No events found in next 14 days — scraper may be producing stale data')
  } catch (e) {
    bad(`Scraper freshness check failed: ${e.message}`)
  }
}

// ── API latency (GAP 10) ──────────────────────────────────────────────────────

function checkApiLatency() {
  section('API Latency (GAP 10)')
  const WARN_MS  = 3000
  const FAIL_MS  = 6000
  let checked = 0, slow = 0
  for (const [url, ms] of Object.entries(timings)) {
    if (!url.startsWith(API)) continue
    checked++
    if (ms > FAIL_MS)      { slow++; bad(`Slow API response ${ms}ms: ${url.replace(API, '')}`) }
    else if (ms > WARN_MS) { slow++; warning(`Elevated API latency ${ms}ms: ${url.replace(API, '')}`) }
  }
  if (checked === 0) warning('No API timings recorded')
  else if (slow === 0)     ok(`All ${checked} timed API calls within latency thresholds`)
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const start = Date.now()
  console.log(`\n🔍 NovaKidLife Site QA — ${new Date().toISOString()}`)
  console.log(`   Mode: ${FAST ? 'fast' : `full (sampling ${SAMPLE_N} slugs)`}`)

  await checkHomepage()
  await checkEventsPage()
  await checkApiEventRendering()
  const slugs = await checkApi()
  await checkStaticPages()
  await checkDescriptionQuality()
  await checkScraperFreshness()
  await checkSeoMetadata()
  if (!FAST && slugs.length > 0) await checkEventSlugs(slugs)
  await checkBlogPages()
  checkApiLatency()   // reads timings collected above — must be last

  const elapsed = ((Date.now() - start) / 1000).toFixed(1)
  console.log(`\n${'═'.repeat(64)}`)
  console.log(`  Results: ✅ ${pass} passed  ❌ ${fail} failed  ⚠️  ${warn} warnings`)
  console.log(`  Time: ${elapsed}s`)

  if (failures.length > 0) {
    console.log(`\n  Failures:`)
    failures.forEach(f => console.log(`    • ${f}`))
  }

  console.log('')
  process.exit(fail > 0 ? 1 : 0)
}

main().catch(e => { console.error(e); process.exit(1) })
