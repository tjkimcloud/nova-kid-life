#!/usr/bin/env node
/**
 * qa-site.js — Comprehensive site QA for novakidlife.com
 *
 * Checks every user-facing concern:
 *  - All pages load without error
 *  - No past/expired events visible
 *  - Registration URLs go to real event pages (not scraped aggregators)
 *  - Event times are not all midnight (scraper timezone issue)
 *  - Images load (not 404)
 *  - All category/tab filters return results
 *  - SEO metadata complete on all key pages
 *  - Description quality (no raw HTML artifacts)
 *  - Blog pages load clean
 *  - API latency within thresholds
 *  - Scraper freshness (events exist in next 14 days)
 *
 * Usage:
 *   node scripts/qa-site.js              # full (samples 30 slugs)
 *   node scripts/qa-site.js --fast       # homepage + API only
 *   node scripts/qa-site.js --sample 50  # check N random event slugs
 *   node scripts/qa-site.js --json       # output failures as JSON for orchestrator
 */

const https = require('https')
const http  = require('http')

const SITE       = 'https://novakidlife.com'
const API        = 'https://api.novakidlife.com'
const FAST       = process.argv.includes('--fast')
const JSON_OUT   = process.argv.includes('--json')
const SAMPLE_IDX = process.argv.indexOf('--sample')
const SAMPLE_N   = SAMPLE_IDX !== -1 ? parseInt(process.argv[SAMPLE_IDX + 1] || '30', 10) : 30

// Known aggregator domains — registration_url should NEVER point here
const AGGREGATORS = [
  'dullesmoms.com', 'patch.com', 'macaronikid.com', 'mommypoppins.com',
  'dcmetromoms.com', 'kidsandkaboodle.com', 'funinfairfaxva.com',
  'connecticutmoms.com', 'everfest.com', 'zvents.com',
]

// Legitimate ticket/registration platforms (NOT aggregators)
const LEGIT_TICKET_SITES = [
  'eventbrite.com', 'meetup.com', 'facebook.com', 'ticketmaster.com',
  'eventive.org', 'universe.com',
]

// ── HTTP helpers ──────────────────────────────────────────────────────────────

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

// HEAD-only fetch to verify a URL returns 200 without downloading the body
function head(url, timeout = 8000) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http
    const options = new URL(url)
    options.method = 'HEAD'
    const req = lib.request({ ...options, method: 'HEAD', headers: { 'User-Agent': 'NovaKidLife-QA/1.0' } }, (res) => {
      res.resume()
      resolve({ status: res.statusCode, location: res.headers['location'] })
    })
    req.on('error', reject)
    req.setTimeout(timeout, () => { req.destroy(); reject(new Error(`Timeout HEAD: ${url}`)) })
    req.end()
  })
}

// ── Result tracking ───────────────────────────────────────────────────────────

let pass = 0, fail = 0, warn = 0
const failures  = []    // { category, message }
const warnings  = []
const timings   = {}

const CATEGORIES = {
  PAST_EVENTS:   'past_events',       // expired/past events still visible
  REG_URLS:      'registration_urls', // URLs pointing to aggregators or 404
  BROKEN_PAGES:  'broken_pages',      // 404 / 500 / "Page not found"
  FILTERS:       'filters',           // category/tab/filter returning 0 results or error
  IMAGES:        'images',            // image URLs 404ing
  TIMES:         'event_times',       // all events at midnight (timezone bug)
  SEO:           'seo',               // missing meta tags
  DESCRIPTIONS:  'descriptions',      // raw HTML artifacts in descriptions
  LATENCY:       'latency',           // slow API responses
  SCRAPER:       'scraper',           // stale data / no upcoming events
}

function ok(msg)            { pass++; if (!JSON_OUT) console.log(`  ✅ ${msg}`) }
function bad(msg, cat)      { fail++; failures.push({ category: cat || 'general', message: msg }); if (!JSON_OUT) console.log(`  ❌ ${msg}`) }
function warning(msg, cat)  { warn++; warnings.push({ category: cat || 'general', message: msg });  if (!JSON_OUT) console.log(`  ⚠️  ${msg}`) }
function section(title)     { if (!JSON_OUT) console.log(`\n── ${title} ${'─'.repeat(Math.max(0, 60 - title.length))}`) }

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

function stripScripts(html) {
  return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
}

function isAggregator(url) {
  if (!url) return false
  return AGGREGATORS.some(a => url.includes(a))
}

// ── Check: Homepage ───────────────────────────────────────────────────────────

async function checkHomepage() {
  section('Homepage')
  try {
    const { status, body } = await timedFetch(SITE)
    if (status !== 200) return bad(`Homepage HTTP ${status}`, CATEGORIES.BROKEN_PAGES)
    ok(`Homepage HTTP 200`)

    const visible = stripScripts(body)
    const checks = [
      ['Hero heading',       'Find something'],
      ['Browse by interest', 'Browse by interest'],
      ['Newsletter section', 'Never Miss'],
    ]
    for (const [label, needle] of checks) {
      if (body.includes(needle)) ok(label)
      else bad(`Homepage — ${label} not found`, CATEGORIES.BROKEN_PAGES)
    }
    if (visible.includes('Page not found'))
      bad(`Homepage shows "Page not found"`, CATEGORIES.BROKEN_PAGES)
    else ok('No "Page not found" on homepage')

    // HTTPS / www redirect
    try {
      const r = await head('http://novakidlife.com')
      if (r.status >= 300 && r.status < 400 && r.location?.includes('https'))
        ok('HTTP → HTTPS redirect works')
      else if (r.status === 200)
        warning('http:// is not redirecting to https:// — CloudFront may be misconfigured')
    } catch { /* ignore — DNS may not resolve http */ }

  } catch (e) {
    bad(`Homepage fetch failed: ${e.message}`, CATEGORIES.BROKEN_PAGES)
  }
}

// ── Check: Events page ────────────────────────────────────────────────────────

async function checkEventsPage() {
  section('Events Page')
  try {
    const { status, body } = await timedFetch(`${SITE}/events`)
    if (status !== 200) return bad(`Events page HTTP ${status}`, CATEGORIES.BROKEN_PAGES)
    ok(`Events page HTTP 200`)
    const visible = stripScripts(body)
    if (visible.includes('Page not found'))
      bad(`Events page shows "Page not found"`, CATEGORIES.BROKEN_PAGES)
    else ok('Events page has no "Page not found"')

    // Note: tabs (Local Events / Deals) are client-rendered — not checkable in static HTML
  } catch (e) {
    bad(`Events page fetch failed: ${e.message}`, CATEGORIES.BROKEN_PAGES)
  }
}

// ── Check: No past events in feed ─────────────────────────────────────────────
// The API should only return events with start_at >= today.
// If past events leak through, parents see stale content and lose trust.

async function checkNoPastEvents() {
  section('Past Events Leak Check')
  try {
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=100&offset=0`)
    if (status !== 200) { bad(`API HTTP ${status}`, CATEGORIES.PAST_EVENTS); return }
    const data = JSON.parse(body)
    const items = data.items ?? []
    if (items.length === 0) { warning('No events returned — cannot check for past events'); return }

    const now = Date.now()
    const pastEvents = items.filter(ev => {
      const t = new Date(ev.start_at).getTime()
      return t < now - 24 * 60 * 60 * 1000   // more than 1 day in the past
    })

    if (pastEvents.length === 0) {
      ok(`No past events in feed (${items.length} events checked)`)
    } else {
      bad(
        `${pastEvents.length} past event(s) visible in feed — users will see expired content`,
        CATEGORIES.PAST_EVENTS
      )
      pastEvents.slice(0, 5).forEach(ev => {
        if (!JSON_OUT) console.log(`     → "${ev.title?.slice(0, 50)}" — started ${ev.start_at}`)
      })
    }

    // Also check: any events where end_at is in the past (should be archived)
    const expiredEndAt = items.filter(ev => {
      if (!ev.end_at) return false
      return new Date(ev.end_at).getTime() < now
    })
    if (expiredEndAt.length > 0) {
      bad(
        `${expiredEndAt.length} event(s) with past end_at still visible — archive migration may need re-run`,
        CATEGORIES.PAST_EVENTS
      )
    } else {
      ok('No events with past end_at in feed')
    }

  } catch (e) {
    bad(`Past events check failed: ${e.message}`, CATEGORIES.PAST_EVENTS)
  }
}

// ── Check: Registration URL quality ──────────────────────────────────────────
// registration_url should send users to the actual event page, NOT back to
// the aggregator site we scraped from. That creates a terrible UX loop.

async function checkRegistrationUrls() {
  section('Registration URL Quality')
  try {
    // Pull a larger sample to get meaningful signal
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=50&offset=0`)
    if (status !== 200) { bad(`API HTTP ${status}`, CATEGORIES.REG_URLS); return }
    const data = JSON.parse(body)
    const items = data.items ?? []

    let goodCount = 0, aggCount = 0, nullCount = 0, deadCount = 0
    const aggExamples = []
    const deadExamples = []

    // Check for aggregator URLs (sync — fast)
    for (const ev of items) {
      const reg = ev.registration_url
      if (!reg) { nullCount++; continue }
      if (isAggregator(reg)) {
        aggCount++
        aggExamples.push({ title: ev.title?.slice(0, 40), url: reg.slice(0, 80) })
      } else {
        goodCount++
      }
    }

    if (aggCount === 0) ok(`No aggregator registration URLs in ${items.length} sampled events`)
    else {
      bad(
        `${aggCount}/${items.length} events have registration_url pointing to aggregator sites`,
        CATEGORIES.REG_URLS
      )
      aggExamples.slice(0, 3).forEach(ex => {
        if (!JSON_OUT) console.log(`     → "${ex.title}" → ${ex.url}`)
      })
    }

    if (nullCount > items.length * 0.5)
      warning(`${nullCount}/${items.length} events have no registration_url — users have no way to learn more`, CATEGORIES.REG_URLS)
    else
      ok(`${goodCount} events have valid registration URLs (${nullCount} have none)`)

    // Spot-check 5 registration URLs actually load (HTTP 200 or redirect)
    const withUrls = items.filter(ev => ev.registration_url && !isAggregator(ev.registration_url))
    const spot = shuffle([...withUrls]).slice(0, 5)
    await Promise.all(spot.map(async (ev) => {
      try {
        const r = await head(ev.registration_url, 8000)
        if (r.status >= 200 && r.status < 400) {
          ok(`registration_url loads OK (${r.status}): "${ev.title?.slice(0, 35)}"`)
        } else {
          deadCount++
          deadExamples.push({ title: ev.title?.slice(0, 40), url: ev.registration_url?.slice(0, 80), status: r.status })
          bad(`registration_url returns HTTP ${r.status}: "${ev.title?.slice(0, 35)}"`, CATEGORIES.REG_URLS)
        }
      } catch {
        // Network errors on spot-checks are warnings, not failures
        warning(`registration_url unreachable: "${ev.title?.slice(0, 35)}"`, CATEGORIES.REG_URLS)
      }
    }))

  } catch (e) {
    bad(`Registration URL check failed: ${e.message}`, CATEGORIES.REG_URLS)
  }
}

// ── Check: Event time sanity ──────────────────────────────────────────────────
// If the scraper didn't capture times, start_at defaults to midnight UTC.
// In ET (UTC-4/5) that becomes 7pm or 8pm — a consistent wrong time.
// Threshold: if >60% of events start exactly at midnight UTC, flag it.

async function checkEventTimes() {
  section('Event Time Sanity')
  try {
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=50&offset=0`)
    if (status !== 200) { bad(`API HTTP ${status}`, CATEGORIES.TIMES); return }
    const data = JSON.parse(body)
    const items = data.items ?? []
    if (items.length === 0) { warning('No events to check times on'); return }

    const midnight = items.filter(ev => ev.start_at?.endsWith('T00:00:00+00:00') || ev.start_at?.endsWith('T00:00:00Z'))
    const pct = midnight.length / items.length

    if (pct < 0.5) {
      ok(`Event times look healthy — only ${midnight.length}/${items.length} (${Math.round(pct*100)}%) are midnight UTC`)
    } else if (pct < 0.8) {
      warning(
        `${midnight.length}/${items.length} events (${Math.round(pct*100)}%) have midnight UTC start times — scraper may not be capturing event times`,
        CATEGORIES.TIMES
      )
    } else {
      bad(
        `${midnight.length}/${items.length} events (${Math.round(pct*100)}%) start at midnight UTC — all times are likely wrong`,
        CATEGORIES.TIMES
      )
    }
  } catch (e) {
    bad(`Event time check failed: ${e.message}`, CATEGORIES.TIMES)
  }
}

// ── Check: Image URLs load ────────────────────────────────────────────────────
// Spot-check that image_url fields actually return a 200. Broken image URLs
// cause blank image boxes across the site.

async function checkImageUrls() {
  section('Image URL Spot-Check')
  try {
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=30&offset=0`)
    if (status !== 200) { bad(`API HTTP ${status}`, CATEGORIES.IMAGES); return }
    const data = JSON.parse(body)
    const items = (data.items ?? []).filter(ev => ev.image_url)

    if (items.length === 0) { warning('No events have image_url — images may not be generating'); return }

    const sample = shuffle([...items]).slice(0, 8)
    let good = 0, broken = 0

    await Promise.all(sample.map(async (ev) => {
      try {
        const r = await head(ev.image_url, 8000)
        if (r.status >= 200 && r.status < 400) {
          good++
        } else {
          broken++
          bad(`image_url returns HTTP ${r.status}: "${ev.title?.slice(0, 40)}"`, CATEGORIES.IMAGES)
          if (!JSON_OUT) console.log(`     → ${ev.image_url?.slice(0, 80)}`)
        }
      } catch {
        broken++
        bad(`image_url unreachable: "${ev.title?.slice(0, 40)}"`, CATEGORIES.IMAGES)
      }
    }))

    if (broken === 0) ok(`All ${good} sampled image URLs return 200`)
    else warning(`${broken}/${sample.length} sampled image URLs are broken`, CATEGORIES.IMAGES)

    // Also check: how many events have NO image at all?
    const noImage = (data.items ?? []).filter(ev => !ev.image_url)
    if (noImage.length > 0)
      warning(`${noImage.length}/${data.items.length} events have no image_url — image pipeline may have gaps`, CATEGORIES.IMAGES)
    else
      ok(`All ${data.items.length} events have an image_url`)

  } catch (e) {
    bad(`Image URL check failed: ${e.message}`, CATEGORIES.IMAGES)
  }
}

// ── Check: All tabs and category filters return results ───────────────────────

async function checkFiltersAndTabs() {
  section('All Filters & Tabs (Events / Deals / Categories)')
  const tests = [
    // Tabs
    { label: 'Local Events tab (event,amusement,seasonal)',
      url: `${API}/events?section=main&event_type=event%2Camusement%2Cseasonal&limit=5` },
    { label: 'Deals & Freebies tab (deal,birthday_freebie,product_drop)',
      url: `${API}/events?section=main&event_type=deal%2Cbirthday_freebie%2Cproduct_drop&limit=5` },
    // Date filters
    { label: 'This Weekend filter',   url: (() => {
        const day = new Date().getDay()
        const toFri = day >= 5 ? 0 : (5 - day)
        const fri = new Date(); fri.setDate(fri.getDate() + toFri)
        const sun = new Date(fri); sun.setDate(fri.getDate() + (day === 0 ? 0 : 2))
        return `${API}/events?section=main&start_date=${fri.toISOString().split('T')[0]}&end_date=${sun.toISOString().split('T')[0]}T23:59:59&limit=5`
      })() },
    { label: 'This Week filter',      url: (() => {
        const today = new Date().toISOString().split('T')[0]
        const end   = new Date(); end.setDate(end.getDate() + 7)
        return `${API}/events?section=main&start_date=${today}&end_date=${end.toISOString().split('T')[0]}T23:59:59&limit=5`
      })() },
    // Free toggle
    { label: 'Free events filter',    url: `${API}/events?section=main&is_free=true&limit=5` },
    // Category filters (maps to tags)
    { label: 'Category: outdoor',     url: `${API}/events?section=main&category=outdoor&limit=5` },
    { label: 'Category: storytime',   url: `${API}/events?section=main&category=storytime&limit=5` },
    { label: 'Category: stem',        url: `${API}/events?section=main&category=stem&limit=5` },
    { label: 'Category: arts-crafts', url: `${API}/events?section=main&category=arts-crafts&limit=5` },
    { label: 'Category: nature',      url: `${API}/events?section=main&category=nature&limit=5` },
    { label: 'Category: community',   url: `${API}/events?section=main&category=community&limit=5` },
    { label: 'Category: sports',      url: `${API}/events?section=main&category=sports&limit=5` },
  ]

  // Run sequentially — parallel requests overwhelm the cold Lambda instance
  // and cause false 500s. Warm Lambda is <500ms; cold start ~3-5s.
  for (const { label, url } of tests) {
    try {
      const { status, body } = await timedFetch(url)
      if (status !== 200) {
        bad(`${label} → API HTTP ${status}`, CATEGORIES.FILTERS)
        continue
      }
      const data = JSON.parse(body)
      if (data.error) {
        bad(`${label} → API error: ${data.error}`, CATEGORIES.FILTERS)
      } else if ((data.total ?? 0) > 0) {
        ok(`${label} → ${data.total} results`)
      } else {
        warning(`${label} → 0 results (users would see empty state)`, CATEGORIES.FILTERS)
      }
    } catch (e) {
      bad(`${label} → ${e.message}`, CATEGORIES.FILTERS)
    }
  }
}

// ── Check: Event detail pages ─────────────────────────────────────────────────

async function checkEventDetailPages(slugs) {
  section(`Event Detail Pages (sampling ${SAMPLE_N} of ${slugs.length})`)
  if (slugs.length === 0) { warning('No slugs to check'); return }

  const sample = shuffle([...slugs]).slice(0, SAMPLE_N)
  let good = 0, broken = 0, errors = 0

  await Promise.all(
    sample.map(async (item) => {
      const slug = typeof item === 'string' ? item : item.slug
      const url = `${SITE}/events/${slug}`
      try {
        const { status, body } = await fetch(url, 15000)
        if (status !== 200) {
          errors++
          bad(`HTTP ${status}: /events/${slug}`, CATEGORIES.BROKEN_PAGES)
          return
        }
        const visible = stripScripts(body)
        if (visible.includes('Page not found')) {
          broken++
          bad(`"Page not found" at /events/${slug}`, CATEGORIES.BROKEN_PAGES)
        } else if (visible.includes('animate-pulse') || body.includes('EventDetailClient')) {
          good++
        } else {
          broken++
          bad(`Unexpected content at /events/${slug}`, CATEGORIES.BROKEN_PAGES)
        }
      } catch (e) {
        errors++
        bad(`Fetch error /events/${slug}: ${e.message}`, CATEGORIES.BROKEN_PAGES)
      }
    })
  )

  if (good > 0) ok(`${good}/${sample.length} event detail pages load correctly`)
  if (broken > 0) bad(`${broken}/${sample.length} event detail pages broken`, CATEGORIES.BROKEN_PAGES)
  if (errors > 0) warning(`${errors}/${sample.length} event detail pages had fetch errors`, CATEGORIES.BROKEN_PAGES)

  // API spot-check: verify event data is actually accessible
  section('API Event Data Spot-Check')
  const spot = shuffle([...slugs]).slice(0, 5)
  await Promise.all(spot.map(async (item) => {
    const slug = typeof item === 'string' ? item : item.slug
    try {
      const { status, body } = await timedFetch(`${API}/events/${slug}`, 10000)
      if (status !== 200) { bad(`API /events/${slug} → HTTP ${status}`, CATEGORIES.BROKEN_PAGES); return }
      const ev = JSON.parse(body)
      if (!ev.title) { bad(`API /events/${slug} missing title`, CATEGORIES.BROKEN_PAGES); return }

      // Check registration URL isn't an aggregator
      if (isAggregator(ev.registration_url)) {
        bad(`"${ev.title?.slice(0, 40)}" — registration_url is aggregator: ${ev.registration_url?.slice(0,60)}`, CATEGORIES.REG_URLS)
      } else {
        ok(`API data OK: "${ev.title?.slice(0, 40)}"`)
      }
    } catch (e) {
      bad(`API spot-check ${slug}: ${e.message}`, CATEGORIES.BROKEN_PAGES)
    }
  }))
}

// ── Check: API health ─────────────────────────────────────────────────────────

async function checkApi() {
  section('API Health')
  try {
    const { status, body } = await timedFetch(`${API}/events?limit=5&section=main`)
    if (status !== 200) return bad(`API /events HTTP ${status}`, CATEGORIES.BROKEN_PAGES)
    const data = JSON.parse(body)
    const count = data.items?.length ?? 0
    if (count > 0) ok(`API /events returned ${count} events (total: ${data.total})`)
    else bad(`API /events returned 0 events`, CATEGORIES.SCRAPER)

    const ev = data.items?.[0]
    if (ev) {
      const fields = ['id', 'slug', 'title', 'start_at', 'location_name']
      const missing = fields.filter(f => !ev[f])
      if (missing.length) bad(`Event missing required fields: ${missing.join(', ')}`, CATEGORIES.BROKEN_PAGES)
      else ok(`Event shape has all required fields`)
    }
  } catch (e) {
    bad(`API /events failed: ${e.message}`, CATEGORIES.BROKEN_PAGES)
  }

  // Sitemap
  try {
    const { status, body } = await timedFetch(`${API}/sitemap`)
    if (status !== 200) { bad(`API /sitemap HTTP ${status}`, CATEGORIES.BROKEN_PAGES); return [] }
    const data = JSON.parse(body)
    const slugs = data.main_events ?? data.main ?? []
    if (slugs.length > 0) ok(`API /sitemap returned ${slugs.length} event slugs`)
    else bad(`API /sitemap returned 0 slugs`, CATEGORIES.SCRAPER)
    return slugs
  } catch (e) {
    bad(`API /sitemap failed: ${e.message}`, CATEGORIES.BROKEN_PAGES)
    return []
  }
}

// ── Check: Static pages ───────────────────────────────────────────────────────

async function checkStaticPages() {
  section('Static Pages')
  const pages = [
    ['/about',          ''],
    ['/pokemon',        ''],
    ['/privacy-policy', ''],
    ['/sitemap.xml',    '<urlset'],
    ['/robots.txt',     'User-Agent'],
    ['/blog',           ''],
  ]
  await Promise.all(pages.map(async ([path, needle]) => {
    try {
      const { status, body } = await timedFetch(`${SITE}${path}`)
      if (status !== 200) bad(`${path} HTTP ${status}`, CATEGORIES.BROKEN_PAGES)
      else if (needle && !body.includes(needle)) warning(`${path} missing expected content ("${needle}")`)
      else {
        const visible = stripScripts(body)
        if (visible.includes('Page not found')) bad(`${path} shows "Page not found"`, CATEGORIES.BROKEN_PAGES)
        else ok(`${path} HTTP 200`)
      }
    } catch (e) {
      bad(`${path} failed: ${e.message}`, CATEGORIES.BROKEN_PAGES)
    }
  }))
}

// ── Check: Description HTML quality ──────────────────────────────────────────

const API_ARTIFACTS = [
  { pattern: /&lt;p&gt;/,   label: 'double-escaped <p>' },
  { pattern: /&lt;\/p&gt;/, label: 'double-escaped </p>' },
  { pattern: /&amp;lt;/,    label: 'triple-escaped entity' },
]

async function checkDescriptionQuality() {
  section('Description HTML Quality')
  try {
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=20&offset=0`)
    if (status !== 200) { bad(`API HTTP ${status}`, CATEGORIES.DESCRIPTIONS); return }
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
        bad(`"${ev.title?.slice(0, 40)}" — ${hits.map(h => h.label).join(', ')}`, CATEGORIES.DESCRIPTIONS)
      } else {
        clean++
      }
    }
    if (dirty === 0) ok(`All ${clean} sampled descriptions are artifact-free`)
  } catch (e) {
    bad(`Description quality check failed: ${e.message}`, CATEGORIES.DESCRIPTIONS)
  }
}

// ── Check: Blog pages ─────────────────────────────────────────────────────────

const RENDER_ARTIFACTS = [
  { pattern: /<p>\s*<h[23]/i,  label: 'heading wrapped in <p>' },
  { pattern: /<p>\s*<hr/i,     label: '<hr> wrapped in <p>' },
  { pattern: /&lt;p&gt;/,      label: 'double-escaped <p> in page source' },
]

async function checkBlogPages() {
  section('Blog Pages')
  try {
    const { status, body } = await timedFetch(`${SITE}/blog`)
    if (status !== 200) return bad(`/blog HTTP ${status}`, CATEGORIES.BROKEN_PAGES)
    ok(`/blog HTTP 200`)
    if (stripScripts(body).includes('Page not found')) bad('/blog shows "Page not found"', CATEGORIES.BROKEN_PAGES)
    else ok('/blog — no "Page not found"')
  } catch (e) { bad(`/blog fetch failed: ${e.message}`, CATEGORIES.BROKEN_PAGES); return }

  try {
    const { status, body } = await timedFetch(`${API}/blog?limit=3`)
    if (status !== 200) { warning(`Blog API HTTP ${status}`); return }
    const data = JSON.parse(body)
    const slugs = (data.items ?? []).map(p => p.slug).filter(Boolean)
    if (slugs.length === 0) { warning('No blog slugs from API'); return }

    await Promise.all(slugs.map(async (slug) => {
      try {
        const { status: s, body: b } = await timedFetch(`${SITE}/blog/${slug}`, 15000)
        if (s !== 200) { bad(`/blog/${slug} HTTP ${s}`, CATEGORIES.BROKEN_PAGES); return }
        const visible = stripScripts(b)
        if (visible.includes('Page not found')) { bad(`/blog/${slug} shows "Page not found"`, CATEGORIES.BROKEN_PAGES); return }
        const hits = RENDER_ARTIFACTS.filter(({ pattern }) => pattern.test(b))
        if (hits.length) bad(`/blog/${slug} — ${hits.map(h => h.label).join(', ')}`, CATEGORIES.DESCRIPTIONS)
        else ok(`/blog/${slug} — clean`)
      } catch (e) {
        bad(`/blog/${slug} failed: ${e.message}`, CATEGORIES.BROKEN_PAGES)
      }
    }))
  } catch (e) {
    warning(`Blog slug check failed: ${e.message}`)
  }
}

// ── Check: SEO metadata ───────────────────────────────────────────────────────

async function checkSeoMetadata() {
  section('SEO Metadata')
  const pages = [
    { url: SITE,             label: 'Homepage' },
    { url: `${SITE}/events`, label: 'Events page' },
    { url: `${SITE}/pokemon`, label: 'Pokémon page' },
  ]
  for (const { url, label } of pages) {
    try {
      const { status, body } = await timedFetch(url)
      if (status !== 200) { bad(`${label} HTTP ${status}`, CATEGORIES.SEO); continue }
      const seoChecks = [
        ['og:title',       /property="og:title"/],
        ['og:image',       /property="og:image"/],
        ['canonical',      /rel="canonical"/],
        ['meta description', /name="description"/],
      ]
      for (const [name, pattern] of seoChecks) {
        if (pattern.test(body)) ok(`${label} — ${name}`)
        else bad(`${label} — missing ${name}`, CATEGORIES.SEO)
      }
    } catch (e) {
      bad(`${label} SEO check failed: ${e.message}`, CATEGORIES.SEO)
    }
  }
}

// ── Check: Scraper freshness ──────────────────────────────────────────────────

async function checkScraperFreshness() {
  section('Scraper Freshness')
  try {
    const { status, body } = await timedFetch(`${API}/events?section=main&limit=50&offset=0`)
    if (status !== 200) { bad(`API HTTP ${status}`, CATEGORIES.SCRAPER); return }
    const data = JSON.parse(body)
    const items = data.items ?? []
    if (items.length === 0) { bad('No events in feed — scraper may be down', CATEGORIES.SCRAPER); return }

    const now = Date.now()
    const twoWeeks = now + 14 * 24 * 60 * 60 * 1000
    const upcoming = items.filter(ev => {
      const t = new Date(ev.start_at).getTime()
      return t > now && t < twoWeeks
    })
    if (upcoming.length > 0) ok(`${upcoming.length} events in next 14 days — scraper is active`)
    else bad('No events found in next 14 days — scraper may be stale or down', CATEGORIES.SCRAPER)

    // Check total event count isn't dropping fast
    if (data.total < 50) warning(`Only ${data.total} total events — unusually low, scraper may have issues`, CATEGORIES.SCRAPER)
    else ok(`${data.total} total events in feed`)
  } catch (e) {
    bad(`Scraper freshness check failed: ${e.message}`, CATEGORIES.SCRAPER)
  }
}

// ── Check: API latency ────────────────────────────────────────────────────────

function checkApiLatency() {
  section('API Latency')
  // Lambda cold starts take 3-5s on first daily invocation — expected.
  // Warm responses should be <1s. Fail threshold is generous for cold starts.
  const WARN_MS = 5000, FAIL_MS = 12000
  let checked = 0, slow = 0
  for (const [url, ms] of Object.entries(timings)) {
    if (!url.startsWith(API)) continue
    checked++
    if (ms > FAIL_MS)      { slow++; bad(`Slow API (${ms}ms): ${url.replace(API, '')}`, CATEGORIES.LATENCY) }
    else if (ms > WARN_MS) { slow++; warning(`Elevated latency (${ms}ms): ${url.replace(API, '')}`, CATEGORIES.LATENCY) }
  }
  if (checked === 0) warning('No API timings recorded')
  else if (slow === 0) ok(`All ${checked} API calls within latency thresholds`)
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const start = Date.now()
  if (!JSON_OUT) {
    console.log(`\n🔍 NovaKidLife Site QA — ${new Date().toISOString()}`)
    console.log(`   Mode: ${FAST ? 'fast' : `full (sampling ${SAMPLE_N} slugs)`}`)
  }

  await checkHomepage()
  await checkEventsPage()
  await checkNoPastEvents()
  await checkEventTimes()
  await checkFiltersAndTabs()
  await checkRegistrationUrls()
  await checkImageUrls()
  const slugs = await checkApi()
  await checkStaticPages()
  await checkDescriptionQuality()
  await checkScraperFreshness()
  await checkSeoMetadata()
  await checkBlogPages()
  if (!FAST && slugs.length > 0) await checkEventDetailPages(slugs)
  checkApiLatency()

  const elapsed = ((Date.now() - start) / 1000).toFixed(1)

  if (JSON_OUT) {
    // Machine-readable output for the orchestrator
    const byCategory = {}
    for (const f of failures) {
      if (!byCategory[f.category]) byCategory[f.category] = []
      byCategory[f.category].push(f.message)
    }
    console.log(JSON.stringify({
      timestamp: new Date().toISOString(),
      pass, fail, warn, elapsed,
      failures: byCategory,
      warnings: warnings.reduce((acc, w) => {
        if (!acc[w.category]) acc[w.category] = []
        acc[w.category].push(w.message)
        return acc
      }, {}),
    }))
  } else {
    console.log(`\n${'═'.repeat(64)}`)
    console.log(`  Results: ✅ ${pass} passed  ❌ ${fail} failed  ⚠️  ${warn} warnings`)
    console.log(`  Time: ${elapsed}s`)
    if (failures.length > 0) {
      console.log(`\n  Failures:`)
      failures.forEach(f => console.log(`    • [${f.category}] ${f.message}`))
    }
    console.log('')
  }

  process.exit(fail > 0 ? 1 : 0)
}

main().catch(e => { console.error(e); process.exit(1) })
