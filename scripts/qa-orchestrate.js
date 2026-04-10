#!/usr/bin/env node
/**
 * qa-orchestrate.js — QA Orchestrator for NovaKidLife
 *
 * This is the daily brain. It runs every morning after the scraper and rebuild,
 * and handles site quality end-to-end without any human prompting:
 *
 *  1. Run full QA audit (qa-site.js --json)
 *  2. If data issues found (past events, expired end_at) → auto-fix (qa-fix-data.js --apply)
 *  3. Re-run QA to verify fixes worked
 *  4. For unfixable issues → open/update a GitHub issue categorized by problem type
 *  5. If all clean → close any open QA issues
 *
 * Categories that get AUTO-FIXED (no human needed):
 *  - past_events: archive stale/expired events from the DB
 *
 * Categories that ALERT HUMAN (open GitHub issue):
 *  - broken_pages: 404s, error pages, "Page not found"
 *  - registration_urls: aggregator URLs or dead registration links
 *  - filters: tab/category filters returning 0 results or errors
 *  - images: broken image URLs
 *  - event_times: all events at midnight (scraper timezone bug)
 *  - descriptions: raw HTML artifacts in event descriptions
 *  - seo: missing meta tags
 *  - latency: slow API responses
 *  - scraper: no upcoming events (scraper may be down)
 *
 * Environment variables required:
 *  - GITHUB_TOKEN      — for opening/closing issues
 *  - GITHUB_REPO       — e.g. "tjkimcloud/nova-kid-life"
 *  - SUPABASE_URL      — for data fixes
 *  - SUPABASE_SERVICE_KEY — service role key
 *  - RUN_URL           — GitHub Actions run URL (optional, for issue links)
 */

const { execSync, spawnSync } = require('child_process')
const https = require('https')
const path  = require('path')

const REPO    = process.env.GITHUB_REPO || 'tjkimcloud/nova-kid-life'
const TOKEN   = process.env.GITHUB_TOKEN
const RUN_URL = process.env.RUN_URL || ''
const SCRIPTS = path.join(__dirname)

// ── GitHub API helper ─────────────────────────────────────────────────────────

function ghApi(method, endpoint, body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.github.com',
      path:     `/repos/${REPO}${endpoint}`,
      method,
      headers: {
        'User-Agent':    'NovaKidLife-QA-Orchestrator/1.0',
        'Authorization': `token ${TOKEN}`,
        'Accept':        'application/vnd.github.v3+json',
        'Content-Type':  'application/json',
      },
    }
    const req = https.request(options, (res) => {
      let data = ''
      res.on('data', d => data += d)
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) })
        } catch { resolve({ status: res.statusCode, data: {} }) }
      })
    })
    req.on('error', reject)
    if (body) req.write(JSON.stringify(body))
    req.end()
  })
}

// ── Run a script and return parsed JSON output ────────────────────────────────

function runScript(scriptPath, args = []) {
  const result = spawnSync('node', [scriptPath, ...args], {
    encoding: 'utf8',
    timeout:  300_000,   // 5 min max
  })
  return { stdout: result.stdout || '', stderr: result.stderr || '', exitCode: result.status ?? 1 }
}

// ── Category → human-readable label ──────────────────────────────────────────

const CATEGORY_LABELS = {
  past_events:       '📅 Past / Expired Events',
  registration_urls: '🔗 Registration URLs (aggregators or broken links)',
  broken_pages:      '💥 Broken Pages (404s, errors)',
  filters:           '🔍 Filters / Tabs Returning No Results',
  images:            '🖼️ Broken Image URLs',
  event_times:       '⏰ Event Times (possible timezone bug)',
  descriptions:      '📝 Description HTML Artifacts',
  seo:               '🔎 Missing SEO Metadata',
  latency:           '🐢 Slow API Responses',
  scraper:           '🤖 Scraper Freshness / Data Volume',
}

// ── Fix priority — these categories get auto-fixed before re-checking ─────────

const AUTO_FIX_CATEGORIES = ['past_events']

// ── GitHub issue management ───────────────────────────────────────────────────

async function getOpenQaIssue() {
  if (!TOKEN) return null
  const { data } = await ghApi('GET', '/issues?labels=qa-failure&state=open&per_page=1')
  return Array.isArray(data) ? data[0] : null
}

async function openOrUpdateIssue(failuresByCategory, warnings, isRecheck = false) {
  if (!TOKEN) { console.log('[orchestrator] No GITHUB_TOKEN — skipping issue management'); return }

  const categoryList = Object.entries(failuresByCategory)
    .map(([cat, msgs]) => {
      const label = CATEGORY_LABELS[cat] || cat
      const items = msgs.slice(0, 5).map(m => `  - ${m}`).join('\n')
      const more  = msgs.length > 5 ? `\n  - ...and ${msgs.length - 5} more` : ''
      return `### ${label} (${msgs.length} failure${msgs.length > 1 ? 's' : ''})\n${items}${more}`
    })
    .join('\n\n')

  const warningList = Object.entries(warnings)
    .map(([cat, msgs]) => `**${CATEGORY_LABELS[cat] || cat}:** ${msgs.slice(0,3).join(', ')}`)
    .join('\n')

  const runLink = RUN_URL ? `\n\n[View full QA run](${RUN_URL})` : ''
  const date    = new Date().toISOString().split('T')[0]
  const totalFails = Object.values(failuresByCategory).reduce((sum, a) => sum + a.length, 0)

  const existing = await getOpenQaIssue()

  if (existing) {
    const commentBody = `## QA ${isRecheck ? 're-check' : 'run'} — still failing (${new Date().toISOString()})

❌ **${totalFails} failures** across ${Object.keys(failuresByCategory).length} categories

${categoryList}

${warningList ? `### Warnings\n${warningList}` : ''}${runLink}`

    await ghApi('POST', `/issues/${existing.number}/comments`, { body: commentBody })
    console.log(`[orchestrator] Updated existing issue #${existing.number}`)
  } else {
    const body = `## Automated QA detected ${totalFails} failure(s) — ${date}

The daily QA audit found issues that require attention. Auto-fixable data issues (past events) have already been addressed. The following require human review:

${categoryList}

${warningList ? `### Warnings (non-blocking)\n${warningList}` : ''}${runLink}

---
### What to check
- **broken_pages**: Visit the listed URLs and verify they load. Check for deployment issues.
- **registration_urls**: Search the DB for events with aggregator registration_urls and update the scraper source config.
- **filters**: Test the tab/category buttons on the live events page. May need API or tag mapping fix.
- **images**: Check image-gen Lambda logs in CloudWatch. May need re-generation run.
- **event_times**: Check scraper source configs for time parsing. All-midnight times mean times aren't being captured.
- **scraper**: Check scraper Lambda CloudWatch logs — it may have failed its last run.

### Next steps
- [ ] Review failures above
- [ ] Fix root cause
- [ ] Close this issue once QA passes clean`

    const { data } = await ghApi('POST', '/issues', {
      title:  `QA Failure — ${totalFails} checks failed (${date})`,
      labels: ['qa-failure'],
      body,
    })
    console.log(`[orchestrator] Opened new issue #${data.number}`)
  }
}

async function closeQaIssue() {
  if (!TOKEN) return
  const existing = await getOpenQaIssue()
  if (!existing) return

  await ghApi('POST', `/issues/${existing.number}/comments`, {
    body: `✅ QA passed clean on ${new Date().toISOString()} — all checks passing. Closing.`,
  })
  await ghApi('PATCH', `/issues/${existing.number}`, { state: 'closed' })
  console.log(`[orchestrator] Closed issue #${existing.number} — all QA passing`)
}

// ── Main orchestration flow ───────────────────────────────────────────────────

async function main() {
  console.log(`\n🎯 NovaKidLife QA Orchestrator — ${new Date().toISOString()}`)
  console.log('   Step 1: Running full QA audit...\n')

  // ── Step 1: Run full QA ───────────────────────────────────────────────────
  const qa1 = runScript(path.join(SCRIPTS, 'qa-site.js'), ['--json', '--sample', '30'])

  // Also capture human-readable output separately for logs
  const qaReadable = runScript(path.join(SCRIPTS, 'qa-site.js'), ['--sample', '30'])
  console.log(qaReadable.stdout)

  let qaResult
  try {
    // qa-site.js --json prints one JSON line to stdout
    const jsonLine = qa1.stdout.trim().split('\n').find(l => l.startsWith('{'))
    qaResult = jsonLine ? JSON.parse(jsonLine) : null
  } catch {
    qaResult = null
  }

  if (!qaResult) {
    console.log('[orchestrator] Could not parse QA JSON output — treating as failure')
    await openOrUpdateIssue(
      { general: ['QA script failed to produce parseable output — check script errors'] },
      {},
    )
    process.exit(1)
  }

  const { failures: failsByCategory, warnings, fail } = qaResult
  console.log(`\n[orchestrator] QA result: ${qaResult.pass} pass / ${fail} fail / ${qaResult.warn} warn`)

  if (fail === 0) {
    console.log('[orchestrator] ✅ All checks passing — closing any open issues')
    await closeQaIssue()
    process.exit(0)
  }

  // ── Step 2: Auto-fix data issues ──────────────────────────────────────────
  const hasAutoFixable = AUTO_FIX_CATEGORIES.some(cat => failsByCategory[cat]?.length > 0)

  if (hasAutoFixable) {
    console.log('\n[orchestrator] Step 2: Auto-fixing data issues...')
    const hasSupabase = process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY

    if (hasSupabase) {
      const fix = runScript(path.join(SCRIPTS, 'qa-fix-data.js'), ['--apply'])
      console.log(fix.stdout)
      if (fix.stderr) console.error(fix.stderr)

      // ── Step 3: Re-run QA to verify fixes ──────────────────────────────────
      console.log('\n[orchestrator] Step 3: Re-running QA to verify fixes...\n')
      const qa2Readable = runScript(path.join(SCRIPTS, 'qa-site.js'), ['--sample', '20'])
      console.log(qa2Readable.stdout)

      const qa2Json = runScript(path.join(SCRIPTS, 'qa-site.js'), ['--json', '--sample', '20'])
      let qa2Result
      try {
        const jsonLine = qa2Json.stdout.trim().split('\n').find(l => l.startsWith('{'))
        qa2Result = jsonLine ? JSON.parse(jsonLine) : null
      } catch { qa2Result = null }

      if (qa2Result && qa2Result.fail === 0) {
        console.log('[orchestrator] ✅ All fixed — closing any open issues')
        await closeQaIssue()
        process.exit(0)
      }

      if (qa2Result) {
        // Report remaining issues after fixes
        const remaining = qa2Result.failures
        const hasRemaining = Object.values(remaining).some(a => a.length > 0)
        if (hasRemaining) {
          console.log(`\n[orchestrator] ${qa2Result.fail} failures remain after auto-fix — alerting`)
          await openOrUpdateIssue(remaining, qa2Result.warnings || {}, true)
        } else {
          await closeQaIssue()
        }
        process.exit(qa2Result.fail > 0 ? 1 : 0)
      }
    } else {
      console.log('[orchestrator] No Supabase credentials — skipping data auto-fix')
    }
  }

  // ── No auto-fixable issues, or no Supabase — just alert ──────────────────
  const hasHumanIssues = Object.keys(failsByCategory).some(
    cat => !AUTO_FIX_CATEGORIES.includes(cat) && failsByCategory[cat]?.length > 0
  )

  if (hasHumanIssues) {
    console.log(`\n[orchestrator] ${fail} failures require human attention — opening/updating issue`)
    await openOrUpdateIssue(failsByCategory, warnings || {})
  }

  process.exit(fail > 0 ? 1 : 0)
}

main().catch(e => {
  console.error('[orchestrator] Fatal error:', e)
  process.exit(1)
})
