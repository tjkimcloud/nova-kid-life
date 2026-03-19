---
name: monitor-api
description: API, Lambda, and database health monitoring for NovaKidLife — Lambda error rates (24h), API Gateway health endpoint, Supabase row counts and recent events check. Run during monitoring sessions or when debugging a suspected API issue.
triggers:
  - API health
  - Lambda errors
  - Supabase health
  - monitor API
  - Lambda error rate
---

# Skill: Monitor — API & Lambda Health

**Run this when:** API is slow, events aren't appearing, or Lambda errors are suspected.

---

## API Health Endpoint

```bash
curl -sf https://api.novakidlife.com/health | jq .
```

Expected: `{"status": "ok"}` with 200. Anything else = Lambda cold start or crash.

---

## Lambda Error Rates (last 24h)

```bash
for fn in api events-scraper image-gen social-poster scheduler; do
  errors=$(aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value="novakidlife-$fn" \
    --start-time "$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)" \
    --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
    --period 86400 \
    --statistics Sum \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo 0)
  echo "$fn errors (24h): ${errors:-0}"
done
```

Any non-zero error count: tail the relevant Lambda's CloudWatch logs immediately.

---

## Tail Lambda Logs

```bash
# API Lambda
aws logs tail /aws/lambda/novakidlife-api --since 30m --follow

# Events scraper
aws logs tail /aws/lambda/novakidlife-events-scraper --since 30m --follow

# Image gen
aws logs tail /aws/lambda/novakidlife-image-gen --since 30m --follow
```

---

## Supabase Health

```bash
# Total event count
curl -s "$SUPABASE_URL/rest/v1/events?select=count" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Prefer: count=exact" \
  -I | grep "content-range"

# Recent events (last 24h) — verify scraper is running
curl -s "$SUPABASE_URL/rest/v1/events?created_at=gte.$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)&select=id,title,created_at&order=created_at.desc&limit=5" \
  -H "apikey: $SUPABASE_ANON_KEY" | jq '.[] | {title, created_at}'
```

If no new events in 24h and scraper shows no errors → check EventBridge trigger schedule in Terraform.
