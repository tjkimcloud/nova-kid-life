# Skill: Scrape Events — Trigger & Monitor

**Purpose:** Trigger and monitor the events scraper Lambda. Covers manual invocation and run monitoring.

**Service:** `services/events-scraper/`

> To add a new source or review architecture — see `scraper-add-source.md`.

---

## Manual Invocation

```bash
# Trigger full scrape (all sources)
aws lambda invoke \
  --function-name novakidlife-events-scraper \
  --payload '{"source": "manual", "targets": ["all"]}' \
  --log-type Tail \
  /tmp/scrape-response.json

# Scrape specific source only
aws lambda invoke \
  --function-name novakidlife-events-scraper \
  --payload '{"source": "manual", "targets": ["fairfax-library"]}' \
  /tmp/response.json

# Scrape all Pokémon sources only
aws lambda invoke \
  --function-name novakidlife-events-scraper \
  --payload '{"source": "manual", "targets": ["pokemon-tcg-nova-events", "pokemon-tcg-drops", "google-news-pokemon-nova"]}' \
  /tmp/response.json

# View response
cat /tmp/scrape-response.json | python -m json.tool
```

---

## Monitor Scrape Progress

```bash
# Tail CloudWatch logs
aws logs tail /aws/lambda/novakidlife-events-scraper \
  --since 30m \
  --follow

# Check SQS queue depth (events waiting for image-gen)
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/<account>/novakidlife-events-queue \
  --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible

# Check DLQ (failed events — investigate if > 0)
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/<account>/novakidlife-events-dlq \
  --attribute-names ApproximateNumberOfMessages
```

---

## Deduplication

Events are deduplicated on `source_url` in Supabase. Re-running the same scraper is safe — no duplicate rows are created. The publisher does `INSERT ... ON CONFLICT (source_url) DO UPDATE SET updated_at = now()`.
