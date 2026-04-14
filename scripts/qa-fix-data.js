#!/usr/bin/env node
/**
 * qa-fix-data.js — Autonomous data cleanup for NovaKidLife
 *
 * Runs automatically from the orchestrator when QA detects stale/expired data.
 * Connects directly to Supabase to archive events that should not be visible.
 *
 * Actions taken (all reversible — only sets status='archived', never deletes):
 *  1. Archive events whose end_at has passed
 *  2. Archive deal/seasonal/product_drop events with start_at > 45 days ago and no end_at
 *  3. Archive events with start_at > 7 days in the past and no end_at (truly past events)
 *
 * Usage:
 *   node scripts/qa-fix-data.js             # dry run (prints what would be archived)
 *   node scripts/qa-fix-data.js --apply     # actually archive
 *   node scripts/qa-fix-data.js --apply --json  # machine-readable output
 */

const https = require('https')

const DRY_RUN   = !process.argv.includes('--apply')
const JSON_OUT  = process.argv.includes('--json')

const SUPABASE_URL     = (process.env.SUPABASE_URL     || '').trim()
const SUPABASE_SERVICE_KEY = (process.env.SUPABASE_SERVICE_KEY || '').trim()  // service role — needed for writes

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
  console.error('Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables')
  process.exit(1)
}

// ── Supabase REST API helper ──────────────────────────────────────────────────

function supabase(path, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${SUPABASE_URL}/rest/v1${path}`)
    const options = {
      hostname: url.hostname,
      path:     url.pathname + url.search,
      method,
      headers: {
        'apikey':        SUPABASE_SERVICE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
        'Content-Type':  'application/json',
        'Prefer':        'return=representation,count=exact',
      },
    }
    const req = https.request(options, (res) => {
      let data = ''
      res.on('data', d => data += d)
      res.on('end', () => {
        try {
          resolve({
            status: res.statusCode,
            count:  parseInt(res.headers['content-range']?.split('/')[1] ?? '0', 10) || 0,
            data:   JSON.parse(data || '[]'),
          })
        } catch {
          resolve({ status: res.statusCode, count: 0, data: [] })
        }
      })
    })
    req.on('error', reject)
    if (body) req.write(JSON.stringify(body))
    req.end()
  })
}

// ── Fix actions ───────────────────────────────────────────────────────────────

const results = { dry_run: DRY_RUN, actions: [] }

function log(msg) { if (!JSON_OUT) console.log(msg) }

async function archiveExpiredEndAt() {
  log('\n── Archive: events with past end_at ─────────────────────────────')
  const now = new Date().toISOString()

  // First: count them
  const check = await supabase(
    `/events?status=eq.published&end_at=lt.${encodeURIComponent(now)}&select=id,title,end_at&limit=100`
  )
  const victims = check.data ?? []

  if (victims.length === 0) {
    log('  ✅ No events with past end_at to archive')
    results.actions.push({ action: 'archive_past_end_at', count: 0 })
    return
  }

  log(`  Found ${victims.length} events with past end_at:`)
  victims.slice(0, 5).forEach(ev =>
    log(`    → "${ev.title?.slice(0, 50)}" (end_at: ${ev.end_at})`)
  )
  if (victims.length > 5) log(`    → ...and ${victims.length - 5} more`)

  if (DRY_RUN) {
    log(`  [DRY RUN] Would archive ${victims.length} events`)
    results.actions.push({ action: 'archive_past_end_at', count: victims.length, dry_run: true })
    return
  }

  const r = await supabase(
    `/events?status=eq.published&end_at=lt.${encodeURIComponent(now)}`,
    'PATCH',
    { status: 'archived' }
  )

  if (r.status >= 200 && r.status < 300) {
    log(`  ✅ Archived ${victims.length} events with past end_at`)
    results.actions.push({ action: 'archive_past_end_at', count: victims.length })
  } else {
    log(`  ❌ Archive failed: HTTP ${r.status}`)
    results.actions.push({ action: 'archive_past_end_at', error: `HTTP ${r.status}` })
  }
}

async function archiveStaleDealEvents() {
  log('\n── Archive: stale deal/seasonal events (no end_at, start > 45d ago) ─')
  const cutoff = new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString()

  const check = await supabase(
    `/events?status=eq.published&start_at=lt.${encodeURIComponent(cutoff)}&end_at=is.null&event_type=in.(deal,seasonal,product_drop)&select=id,title,start_at,event_type&limit=100`
  )
  const victims = check.data ?? []

  if (victims.length === 0) {
    log('  ✅ No stale deal events to archive')
    results.actions.push({ action: 'archive_stale_deals', count: 0 })
    return
  }

  log(`  Found ${victims.length} stale deal/seasonal events:`)
  victims.slice(0, 5).forEach(ev =>
    log(`    → [${ev.event_type}] "${ev.title?.slice(0, 50)}" (started: ${ev.start_at?.slice(0,10)})`)
  )
  if (victims.length > 5) log(`    → ...and ${victims.length - 5} more`)

  if (DRY_RUN) {
    log(`  [DRY RUN] Would archive ${victims.length} stale deal events`)
    results.actions.push({ action: 'archive_stale_deals', count: victims.length, dry_run: true })
    return
  }

  const r = await supabase(
    `/events?status=eq.published&start_at=lt.${encodeURIComponent(cutoff)}&end_at=is.null&event_type=in.(deal,seasonal,product_drop)`,
    'PATCH',
    { status: 'archived' }
  )

  if (r.status >= 200 && r.status < 300) {
    log(`  ✅ Archived ${victims.length} stale deal events`)
    results.actions.push({ action: 'archive_stale_deals', count: victims.length })
  } else {
    log(`  ❌ Archive failed: HTTP ${r.status}`)
    results.actions.push({ action: 'archive_stale_deals', error: `HTTP ${r.status}` })
  }
}

async function archiveTrulyPastEvents() {
  log('\n── Archive: regular events started > 7 days ago with no end_at ────')
  const cutoff = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()

  const check = await supabase(
    `/events?status=eq.published&start_at=lt.${encodeURIComponent(cutoff)}&end_at=is.null&event_type=in.(event,amusement,pokemon_tcg)&select=id,title,start_at,event_type&limit=100`
  )
  const victims = check.data ?? []

  if (victims.length === 0) {
    log('  ✅ No truly past events to archive')
    results.actions.push({ action: 'archive_past_events', count: 0 })
    return
  }

  log(`  Found ${victims.length} events started > 7 days ago with no end_at:`)
  victims.slice(0, 5).forEach(ev =>
    log(`    → [${ev.event_type}] "${ev.title?.slice(0, 50)}" (started: ${ev.start_at?.slice(0,10)})`)
  )
  if (victims.length > 5) log(`    → ...and ${victims.length - 5} more`)

  if (DRY_RUN) {
    log(`  [DRY RUN] Would archive ${victims.length} past events`)
    results.actions.push({ action: 'archive_past_events', count: victims.length, dry_run: true })
    return
  }

  const r = await supabase(
    `/events?status=eq.published&start_at=lt.${encodeURIComponent(cutoff)}&end_at=is.null&event_type=in.(event,amusement,pokemon_tcg)`,
    'PATCH',
    { status: 'archived' }
  )

  if (r.status >= 200 && r.status < 300) {
    log(`  ✅ Archived ${victims.length} past events`)
    results.actions.push({ action: 'archive_past_events', count: victims.length })
  } else {
    log(`  ❌ Archive failed: HTTP ${r.status}`)
    results.actions.push({ action: 'archive_past_events', error: `HTTP ${r.status}` })
  }
}

async function patchKnownBadEvents() {
  log('\n── Patch: known events with wrong date/time or missing registration URL ─')
  // Hand-curated list of events that were scraped with wrong data.
  // Each entry: { slug, patch } where patch is the corrected fields.
  const PATCHES = [
    {
      // Celebrate Reston! — scraped with 1pm EDT time; correct is 12pm EDT.
      // Correct data from restonmuseum.org: Apr 18 12pm-4pm EDT, Lake Anne Plaza.
      slug: 'celebrate-reston-lake-anne-plaza-edacfc',
      patch: {
        title:            'Celebrate Reston!',
        start_at:         '2026-04-18T16:00:00+00:00',   // 12pm EDT = 16:00 UTC
        end_at:           '2026-04-18T20:00:00+00:00',   // 4pm EDT  = 20:00 UTC
        venue_name:       'Lake Anne Plaza',
        address:          '1639 Washington Plaza North, Reston, VA 20190',
        location_text:    'Lake Anne Plaza, Reston, VA',
        lat:              38.9688567,
        lng:              -77.3402978,
        registration_url: 'https://www.restonmuseum.org/events/celebrate-reston-1',
        full_description: 'Celebrate Reston! (Formerly Founder\'s Day) celebrates 22 years and Reston celebrates its 62nd! Live, Work, Play Bob Simon\'s Way. Come to Lake Anne Plaza to enjoy community performances, a book fair with local authors, organizations and vendors, exhibits, and family-friendly activities. Free and open to all ages.',
        is_free:          true,
        source_name:      'reston-museum',
      },
    },
    {
      // Wrong-date duplicate — scraped with April 25 date; archive it.
      slug: 'celebrate-reston-125743',
      archive: true,
    },
  ]

  for (const entry of PATCHES) {
    const { slug, patch, archive } = entry
    // Check if this event exists
    const check = await supabase(`/events?slug=eq.${slug}&status=eq.published&select=slug,title,start_at,registration_url&limit=1`)
    const existing = check.data?.[0]
    if (!existing) {
      log(`  Skipping ${slug} — not found or already archived`)
      continue
    }
    log(`  Found: "${existing.title}" | current start_at: ${existing.start_at?.slice(0,16)} | reg_url: ${existing.registration_url || 'none'}`)

    if (DRY_RUN) {
      const action = archive ? 'archive' : 'patch'
      log(`  [DRY RUN] Would ${action} ${slug}`)
      results.actions.push({ action: 'patch_known_bad', slug, dry_run: true })
      continue
    }

    const payload = archive ? { status: 'archived' } : patch
    const r = await supabase(`/events?slug=eq.${slug}`, 'PATCH', payload)
    if (r.status >= 200 && r.status < 300) {
      log(`  ${archive ? 'Archived' : 'Patched'} ${slug}`)
      results.actions.push({ action: 'patch_known_bad', slug, patched: true })
    } else {
      log(`  Failed to update ${slug}: HTTP ${r.status}`)
      results.actions.push({ action: 'patch_known_bad', slug, error: `HTTP ${r.status}` })
    }
  }
}

async function archiveGhostEvents() {
  log('\n── Archive: ghost events (midnight time + no registration URL) ──────')
  // "Ghost events" come from news homepage sources (ffxnow, arlnow, etc.).
  // They have wrong/missing times (midnight) and no CTA link for users.
  // Criteria: published, no registration_url, start_at on the hour at midnight UTC offsets.
  const check = await supabase(
    `/events?status=eq.published&registration_url=is.null&select=id,slug,title,start_at,source_name&limit=200`
  )
  const candidates = check.data ?? []

  // Filter to midnight-time events (00:00:00 or 04:00:00 UTC = midnight ET)
  const ghosts = candidates.filter(ev => {
    if (!ev.start_at) return false
    const t = ev.start_at
    return t.includes('T00:00:00') || t.includes('T04:00:00') || t.includes('T05:00:00')
  })

  if (ghosts.length === 0) {
    log('  No ghost events to archive')
    results.actions.push({ action: 'archive_ghost_events', count: 0 })
    return
  }

  log(`  Found ${ghosts.length} ghost events (midnight + no registration URL):`)
  ghosts.slice(0, 8).forEach(ev =>
    log(`    → "${ev.title?.slice(0, 55)}" [${ev.source_name}] (${ev.start_at?.slice(0,16)})`)
  )
  if (ghosts.length > 8) log(`    → ...and ${ghosts.length - 8} more`)

  if (DRY_RUN) {
    log(`  [DRY RUN] Would archive ${ghosts.length} ghost events`)
    results.actions.push({ action: 'archive_ghost_events', count: ghosts.length, dry_run: true })
    return
  }

  const slugList = ghosts.map(ev => ev.slug).filter(Boolean)
  if (slugList.length === 0) { results.actions.push({ action: 'archive_ghost_events', count: 0 }); return }

  const r = await supabase(
    `/events?slug=in.(${slugList.join(',')})`,
    'PATCH',
    { status: 'archived' }
  )

  if (r.status >= 200 && r.status < 300) {
    log(`  Archived ${ghosts.length} ghost events`)
    results.actions.push({ action: 'archive_ghost_events', count: ghosts.length })
  } else {
    log(`  Archive failed: HTTP ${r.status}`)
    results.actions.push({ action: 'archive_ghost_events', error: `HTTP ${r.status}` })
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  log(`\n🔧 NovaKidLife Data Fix — ${new Date().toISOString()}`)
  log(`   Mode: ${DRY_RUN ? 'DRY RUN (pass --apply to actually archive)' : 'LIVE — archiving events'}`)

  await patchKnownBadEvents()
  await archiveExpiredEndAt()
  await archiveStaleDealEvents()
  await archiveTrulyPastEvents()
  await archiveGhostEvents()

  const totalFixed = results.actions.reduce((sum, a) => sum + (a.count || 0), 0)
  log(`\n  Total archived: ${totalFixed} events`)

  if (JSON_OUT) {
    console.log(JSON.stringify({ ...results, total_fixed: totalFixed }))
  }

  process.exit(0)
}

main().catch(e => {
  console.error(e)
  process.exit(1)
})
