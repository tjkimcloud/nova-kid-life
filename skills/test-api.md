# Skill: Test API Endpoints

**Purpose:** Smoke-test and validate API Gateway + Lambda REST endpoints.

## Base URL
- Production: `https://api.novakidlife.com`
- Local (SAM): `http://localhost:3001`

## Health Check
```bash
curl -s https://api.novakidlife.com/health | jq .
# Expected: {"status": "ok", "timestamp": "..."}
```

## Events API

### List events
```bash
curl -s "https://api.novakidlife.com/events?limit=10&page=1" | jq .
```

### List with filters
```bash
# By date range
curl -s "https://api.novakidlife.com/events?start_after=2026-03-01&start_before=2026-03-31" | jq .

# By location/radius
curl -s "https://api.novakidlife.com/events?lat=38.8462&lng=-77.3064&radius_miles=10" | jq .

# By age range
curl -s "https://api.novakidlife.com/events?age_min=3&age_max=8" | jq .
```

### Get single event
```bash
curl -s "https://api.novakidlife.com/events/<slug>" | jq .
```

### Semantic search
```bash
curl -s -X POST "https://api.novakidlife.com/events/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "outdoor activities for toddlers", "limit": 5}' | jq .
```

## Expected Response Schema
```json
{
  "data": [
    {
      "id": "uuid",
      "slug": "fairfax-fall-festival-2026",
      "title": "Fairfax Fall Festival",
      "short_description": "...",
      "start_at": "2026-10-15T10:00:00Z",
      "end_at": "2026-10-15T18:00:00Z",
      "location": "Fairfax City, VA",
      "image_url": "https://media.novakidlife.com/...",
      "age_range": "All ages",
      "tags": ["festival", "outdoor"],
      "source_url": "https://..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 142,
    "has_more": true
  }
}
```

## Assert with jq
```bash
# Verify response has data array
curl -s "https://api.novakidlife.com/events" | jq '.data | length > 0'

# Verify all events have required fields
curl -s "https://api.novakidlife.com/events" | \
  jq '.data[] | {has_title: (.title != null), has_start: (.start_at != null)} | select(.has_title == false or .has_start == false)'
```
Empty output = all events valid.

## Local Testing with SAM
```bash
cd services/api
sam local start-api --port 3001

# Then run curl commands against http://localhost:3001
```

## Load Test (quick)
```bash
# 10 concurrent requests
for i in $(seq 1 10); do
  curl -s "https://api.novakidlife.com/events" > /dev/null &
done
wait
echo "Done"
```

## Check Lambda Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=novakidlife-api \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum | jq '.Datapoints[0].Sum'
```
