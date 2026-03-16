# Skill: Monitor System Health

**Purpose:** Check health of all NovaKidLife system components.

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

## Supabase Health

```bash
# Row counts
curl -s "$SUPABASE_URL/rest/v1/events?select=count" \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Prefer: count=exact" \
  -I | grep "content-range"

# Recent events (last 24h)
curl -s "$SUPABASE_URL/rest/v1/events?created_at=gte.$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)&select=id,title,created_at&order=created_at.desc&limit=5" \
  -H "apikey: $SUPABASE_ANON_KEY" | jq '.[] | {title, created_at}'
```

## CloudFront Cache Hit Rate

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name CacheHitRate \
  --dimensions Name=DistributionId,Value="$CLOUDFRONT_DIST_ID" Name=Region,Value=Global \
  --start-time "$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --period 86400 \
  --statistics Average \
  --query 'Datapoints[0].Average'
```
Target: ≥ 85% cache hit rate.

## DLQ Alert
```bash
# If DLQ has messages, investigate immediately
DLQ_DEPTH=$(aws sqs get-queue-attributes \
  --queue-url "https://sqs.us-east-1.amazonaws.com/$(aws sts get-caller-identity --query Account --output text)/novakidlife-events-dlq" \
  --attribute-names ApproximateNumberOfMessages \
  --query Attributes.ApproximateNumberOfMessages --output text)

if [ "$DLQ_DEPTH" -gt 0 ]; then
  echo "WARNING: $DLQ_DEPTH messages in DLQ"
  aws logs tail /aws/lambda/novakidlife-events-scraper --since 6h | grep ERROR
fi
```

## Cost Monitor (this month)

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost' | jq .
```

## Status Dashboard
CloudWatch dashboard: `novakidlife-prod`
```bash
aws cloudwatch get-dashboard --dashboard-name novakidlife-prod | jq .DashboardBody | python3 -m json.tool
```
