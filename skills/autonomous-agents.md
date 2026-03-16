# Skill: Autonomous Agent Architecture — NovaKidLife

**Purpose:** Document the full autonomous operation vision for NovaKidLife — what runs automatically, what triggers it, how failures are handled, and where human review is needed. The goal is a system that discovers, enriches, publishes, and promotes family events with zero daily intervention.

---

## Autonomous Operation Vision

NovaKidLife runs as a self-sustaining content pipeline:

```
[World: 59+ event sources update daily]
         │
         ▼
[Scraper Agent — daily 6am EST]
  Discovers new events across all sources
         │
         ▼
[Event Queue — SQS]
  Buffers new events for processing
         │
         ├──► [Image Gen Agent — SQS trigger]
         │      Sources/generates images, warm-grades, uploads to CDN
         │      Updates all 10 image columns in Supabase
         │
         ├──► [Content Enrichment — future agent]
         │      Generates full_description, short_description, FAQ content
         │      Marks event status = 'published'
         │
         └──► [Social Poster Agent — SQS trigger]
                Schedules platform-optimized posts via Buffer
                Respects cadence limits (1 post/event/platform)
         │
         ▼
[Monitoring — CloudWatch + SNS]
  Alerts on failures, DLQ depth, error rates
         │
         ▼
[You — receive SNS alert only if something breaks]
```

---

## Scheduled Triggers (EventBridge)

| Schedule | Lambda | Action |
|----------|--------|--------|
| Daily 6:00 AM EST | `events-scraper` | Run all 4 tiers, publish to SQS |
| Daily 8:00 AM EST | `social-poster` | Post morning scheduled content |
| Daily 12:00 PM EST | `social-poster` | Post midday scheduled content |
| Daily 5:00 PM EST | `social-poster` | Post evening scheduled content |
| Saturday 10:00 AM | `social-poster` | Weekend roundup post |

---

## Event Lifecycle (automated)

```
1. SCRAPED     → RawEvent found by scraper, published to SQS
2. QUEUED      → SQS message received by image-gen Lambda
3. ENRICHED    → Images generated, alt text created, all columns updated
4. PUBLISHED   → status = 'published', visible on frontend
5. PROMOTED    → Social posts scheduled via Buffer
6. ARCHIVED    → past events auto-archived (status = 'archived')
```

### Status transitions
```sql
-- Auto-archive past events (could be a nightly Lambda or DB trigger)
UPDATE events
SET status = 'archived'
WHERE status = 'published'
  AND start_at < NOW() - INTERVAL '2 days';
```

---

## Failure Handling

### SQS Dead Letter Queues
Each processing queue has a DLQ. Messages land in DLQ after 3 failed processing attempts.

| Queue | DLQ | CloudWatch Alarm |
|-------|-----|-----------------|
| `novakidlife-events-queue` | `novakidlife-events-dlq` | DLQ depth > 0 → SNS alert |
| `novakidlife-social-queue` | `novakidlife-social-dlq` | DLQ depth > 0 → SNS alert |

### Lambda error alarms
```
Lambda error rate > 5% → SNS email alert
Lambda duration p99 > 60s → SNS alert
API 5xx rate > 1% → SNS alert
```

### Graceful degradation
- Image gen fails → event published with `image_url = null` (placeholder shown)
- Social poster fails → post goes to DLQ, manual review via Buffer dashboard
- Scraper source fails → logged, other sources continue, alert if >20% sources fail
- API Lambda fails → static export still serves cached HTML (CloudFront cache)

---

## Human-in-the-Loop Touchpoints

The system is designed to be fully hands-off. The only situations requiring human input:

| Situation | Action Required | Frequency |
|-----------|----------------|-----------|
| SNS failure alert | Check CloudWatch logs, redrive DLQ | Rare (< once/week) |
| New scrape source to add | Add 1 JSON entry to `config/sources.json` | Occasional |
| Buffer post needs editing | Edit directly in Buffer dashboard | Optional |
| New Pokémon set releases | Verify drops scraper caught it | Monthly |
| Lighthouse score drops | Check CI report, fix perf issue | Per deploy |
| DNS / SSL renewal | Managed by ACM (auto-renew) | Never |

---

## Monitoring Dashboard (CloudWatch — Session 12)

**`novakidlife-prod` dashboard widgets:**
```
Row 1: Lambda invocations × 4 (scraper, image-gen, api, social-poster)
Row 2: Lambda error rates × 4
Row 3: SQS queue depths (events-queue, social-queue)
Row 4: SQS DLQ depths (events-dlq, social-dlq)
Row 5: API Gateway 4xx + 5xx rates
Row 6: CloudFront cache hit rate + origin latency
```

**SNS alert channels:**
- Email: your email for all P1 alerts
- SMS: your phone for Lambda error rate > 10%

---

## Future Autonomous Agents (Post-Launch)

### Content enrichment agent
AI-powered enrichment Lambda that:
- Generates `full_description` from scraped raw text (gpt-4o-mini)
- Generates `short_description` (≤120 chars)
- Extracts/validates age range from description
- Sets `is_free` and `cost_description` accurately
- Triggers after scraper publishes to SQS, before image gen

### Newsletter agent
Weekly automated email:
- Selects top 5 free events for coming weekend
- Generates roundup copy (using content-generation skill)
- Sends via SendGrid/Mailchimp to newsletter_subs list
- Triggered: Friday 9am EventBridge rule

### Trend monitoring agent
Weekly intelligence:
- Monitors competitor sites (dullesmoms, Washingtonian Kids) for coverage gaps
- Tracks which event types drive most page views (via GA4 API)
- Sends summary to SNS topic (your email) every Monday
- Suggests new scrape sources if coverage gaps found

### Facebook/Nextdoor agent (deferred — see memory)
- Playwright-based scraper for logged-in social platforms
- Requires ToS review before implementation
- Human-in-the-loop curation step required

---

## MCP Integration (Future)

Once MCPs are built (see `skills/mcp-builder.md`), the autonomous loop can be extended:

```
Claude (via MCP) can:
  → Query live events ("what's happening in Reston this weekend?")
  → Trigger scrape for a specific source
  → Review and approve social posts before sending
  → Add a new scrape source to sources.json
  → Archive stale events
  → Pull CloudWatch metrics on demand
```

---

## Key Operational Commands

```powershell
# Check what's in the events queue
# (requires AWS CLI configured)
aws sqs get-queue-attributes --queue-url [queue-url] --attribute-names All

# Redrive DLQ back to main queue (after fixing root cause)
aws sqs start-message-move-task --source-arn [dlq-arn] --destination-arn [queue-arn]

# Manually trigger scraper
aws lambda invoke --function-name novakidlife-events-scraper /dev/null

# Check Lambda logs
aws logs tail /aws/lambda/novakidlife-events-scraper --follow
```
