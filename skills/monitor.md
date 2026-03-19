# Skill: Monitor System Health

**Purpose:** Quick full-system health check. Runs all components in one pass.

> For detailed API/Lambda/Supabase diagnostics — see `monitor-api.md`.
> For SQS, CloudFront, DLQ, and cost monitoring — see `monitor-infra.md`.

---

## Quick Health Check (run all)

```bash
echo "=== API Health ===" && curl -sf https://api.novakidlife.com/health | jq .
echo "=== Frontend ===" && curl -sI https://novakidlife.com | grep -E "HTTP|x-cache|age:"
echo "=== SQS Queue Depths ===" && bash -c '
  for q in events-queue social-queue events-dlq; do
    echo -n "$q: "
    aws sqs get-queue-attributes \
      --queue-url "https://sqs.us-east-1.amazonaws.com/$(aws sts get-caller-identity --query Account --output text)/novakidlife-$q" \
      --attribute-names ApproximateNumberOfMessages \
      --query Attributes.ApproximateNumberOfMessages \
      --output text
  done
'
```

Expected healthy state:
- API: `{"status": "ok"}`
- Frontend: `HTTP/2 200` + `x-cache: Hit from cloudfront`
- `events-queue` and `social-queue`: 0 (or low — normal during active scrape)
- `events-dlq`: **must be 0** — any messages here require investigation
