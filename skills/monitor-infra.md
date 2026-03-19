---
name: monitor-infra
description: Infrastructure health monitoring for NovaKidLife — SQS queue depths, DLQ alert, CloudFront cache hit rate, AWS cost monitor, and CloudWatch dashboard. Run during infra sessions or when events are getting lost in the pipeline.
triggers:
  - SQS
  - queue depth
  - DLQ
  - CloudFront
  - cache hit rate
  - cost monitor
  - CloudWatch dashboard
  - monitor infra
---

# Skill: Monitor — Infrastructure Health

**Run this when:** Events are disappearing mid-pipeline, CloudFront is slow, or checking monthly costs.

---

## SQS Queue Depths

```bash
for q in events-queue social-queue events-dlq; do
  echo -n "$q: "
  aws sqs get-queue-attributes \
    --queue-url "https://sqs.us-east-1.amazonaws.com/$(aws sts get-caller-identity --query Account --output text)/novakidlife-$q" \
    --attribute-names ApproximateNumberOfMessages \
    --query Attributes.ApproximateNumberOfMessages \
    --output text
done
```

- `events-queue` depth > 0 after scraper finishes → image-gen Lambda may be backed up (normal) or failing (check DLQ)
- `events-dlq` depth > 0 → **investigate immediately**

---

## DLQ Alert

```bash
DLQ_DEPTH=$(aws sqs get-queue-attributes \
  --queue-url "https://sqs.us-east-1.amazonaws.com/$(aws sts get-caller-identity --query Account --output text)/novakidlife-events-dlq" \
  --attribute-names ApproximateNumberOfMessages \
  --query Attributes.ApproximateNumberOfMessages --output text)

if [ "$DLQ_DEPTH" -gt 0 ]; then
  echo "WARNING: $DLQ_DEPTH messages in DLQ"
  aws logs tail /aws/lambda/novakidlife-events-scraper --since 6h | grep ERROR
fi
```

DLQ messages = events that failed all 3 retry attempts. Check the error logs and fix the root cause before reprocessing.

---

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

**Target: ≥ 85% cache hit rate.** Below 70% = check CloudFront behavior rules in Terraform (may have query string caching misconfigured).

---

## Frontend Reachability

```bash
curl -sI https://novakidlife.com | grep -E "HTTP|x-cache|age:"
```

`x-cache: Hit from cloudfront` = serving from cache (correct).
`x-cache: Miss from cloudfront` = cache busted or first request after invalidation.

---

## Cost Monitor (this month)

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost' | jq .
```

---

## CloudWatch Dashboard

```bash
aws cloudwatch get-dashboard --dashboard-name novakidlife-prod | jq .DashboardBody | python3 -m json.tool
```

Dashboard URL in AWS Console: CloudWatch → Dashboards → `novakidlife-prod`
