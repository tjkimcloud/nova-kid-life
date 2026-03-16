# API Contracts — NovaKidLife

**Base URL:** `https://api.novakidlife.com`
**Format:** JSON (`Content-Type: application/json`)
**Auth:** Public routes — none. Admin routes — `x-api-key: <key>` header.

---

## Public Endpoints

---

### 1. `GET /health`
System health check.

**Response `200`:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-13T06:00:00Z",
  "version": "1.0.0"
}
```

---

### 2. `GET /events`
List published events with optional filters. Results sorted by `start_at` ascending.

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (default: 1) |
| `limit` | int | Results per page (default: 20, max: 100) |
| `start_after` | ISO8601 | Events starting after this datetime |
| `start_before` | ISO8601 | Events starting before this datetime |
| `lat` | float | Latitude for radius search |
| `lng` | float | Longitude for radius search |
| `radius_miles` | float | Search radius in miles (default: 25) |
| `age_min` | int | Minimum child age (years) |
| `age_max` | int | Maximum child age (years) |
| `tags` | string | Comma-separated tags to filter by |
| `category` | string | Category slug |
| `free_only` | bool | Only free events |

**Response `200`:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "slug": "fairfax-fall-festival-2026-10-15",
      "title": "Fairfax Fall Festival",
      "short_description": "Annual harvest celebration with pumpkin patch and hayrides.",
      "start_at": "2026-10-15T10:00:00Z",
      "end_at": "2026-10-15T18:00:00Z",
      "location": "Fairfax City, VA",
      "lat": 38.8462,
      "lng": -77.3064,
      "image_url": "https://media.novakidlife.com/events/550e8400/hero.webp",
      "age_range": "All ages",
      "tags": ["festival", "outdoor", "seasonal"],
      "is_free": false,
      "source_url": "https://fairfaxcity.gov/events/fall-festival"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 142,
    "has_more": true
  }
}
```

**Error `400`:** Invalid query parameter values.

---

### 3. `GET /events/{slug}`
Single event by slug.

**Path Parameters:**
- `slug` — URL-safe event identifier

**Response `200`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "fairfax-fall-festival-2026-10-15",
  "title": "Fairfax Fall Festival",
  "short_description": "Annual harvest celebration with pumpkin patch and hayrides.",
  "full_description": "Join us for the annual Fairfax Fall Festival...",
  "start_at": "2026-10-15T10:00:00Z",
  "end_at": "2026-10-15T18:00:00Z",
  "location": "Fairfax City, VA",
  "lat": 38.8462,
  "lng": -77.3064,
  "image_url": "https://media.novakidlife.com/events/550e8400/hero.webp",
  "age_range": "All ages",
  "tags": ["festival", "outdoor", "seasonal"],
  "is_free": false,
  "cost_description": "$5/person, under 2 free",
  "registration_url": "https://fairfaxcity.gov/events/fall-festival/register",
  "source_url": "https://fairfaxcity.gov/events/fall-festival",
  "seo_title": "Fairfax Fall Festival 2026 | Family Events | NovaKidLife",
  "seo_description": "Enjoy the annual Fairfax Fall Festival with pumpkin patch, hayrides...",
  "created_at": "2026-03-13T06:05:00Z",
  "updated_at": "2026-03-13T06:10:00Z"
}
```

**Error `404`:**
```json
{ "error": "Event not found", "slug": "fairfax-fall-festival-2026-10-15" }
```

---

### 4. `POST /events/search`
Semantic search using pgvector similarity (finds conceptually similar events even without keyword match).

**Request body:**
```json
{
  "query": "outdoor activities for toddlers",
  "limit": 10,
  "start_after": "2026-03-13T00:00:00Z"
}
```

**Response `200`:**
```json
{
  "data": [ /* same shape as /events items */ ],
  "query": "outdoor activities for toddlers",
  "total": 8
}
```

---

### 5. `GET /events/featured`
Editorially featured events (admin-curated or highest engagement). Returns up to 6 events.

**Response `200`:**
```json
{
  "data": [ /* same shape as /events items, max 6 */ ]
}
```

---

### 6. `GET /events/upcoming`
Next 7 days of events, sorted by `start_at`. Returns up to 20.

**Query Parameters:** `lat`, `lng`, `radius_miles` (optional, same as `/events`)

**Response `200`:**
```json
{
  "data": [ /* same shape as /events items */ ],
  "window": {
    "start": "2026-03-13T00:00:00Z",
    "end": "2026-03-20T23:59:59Z"
  }
}
```

---

### 7. `GET /categories`
All event categories with event counts.

**Response `200`:**
```json
{
  "data": [
    { "slug": "outdoor", "name": "Outdoor", "count": 42, "icon": "🌳" },
    { "slug": "arts-crafts", "name": "Arts & Crafts", "count": 18, "icon": "🎨" },
    { "slug": "sports", "name": "Sports & Fitness", "count": 31, "icon": "⚽" },
    { "slug": "educational", "name": "Educational", "count": 27, "icon": "📚" },
    { "slug": "free", "name": "Free Events", "count": 56, "icon": "🎉" }
  ]
}
```

---

### 8. `GET /locations`
NoVa locations (counties + cities) with event counts.

**Response `200`:**
```json
{
  "data": [
    { "slug": "fairfax", "name": "Fairfax County", "type": "county", "count": 58 },
    { "slug": "arlington", "name": "Arlington", "type": "county", "count": 34 },
    { "slug": "loudoun", "name": "Loudoun County", "type": "county", "count": 29 },
    { "slug": "prince-william", "name": "Prince William County", "type": "county", "count": 21 }
  ]
}
```

---

### 9. `POST /newsletter/subscribe`
Subscribe to the NovaKidLife weekly newsletter.

**Request body:**
```json
{
  "email": "parent@example.com",
  "zip_code": "22101",
  "frequency": "weekly"
}
```

**Response `201`:**
```json
{ "status": "subscribed", "email": "parent@example.com" }
```

**Error `409`:** Already subscribed.
**Error `422`:** Invalid email format.

---

### 10. `GET /sitemap`
All published event slugs and last-modified dates for sitemap generation.

**Response `200`:**
```json
{
  "events": [
    { "slug": "fairfax-fall-festival-2026-10-15", "updated_at": "2026-03-13T06:10:00Z" }
  ],
  "generated_at": "2026-03-13T07:00:00Z"
}
```

---

## Admin Endpoints (API Key Required)

Header: `x-api-key: <ADMIN_API_KEY>`

---

### 11. `POST /admin/events/trigger-scrape`
Manually trigger the events scraper Lambda.

**Request body:**
```json
{
  "targets": ["all"],
  "dry_run": false
}
```

**Response `202`:**
```json
{
  "status": "triggered",
  "invocation_id": "abc123",
  "targets": ["all"]
}
```

---

### 12. `GET /admin/health/detailed`
Detailed system health: Lambda status, SQS queue depths, Supabase row counts.

**Response `200`:**
```json
{
  "status": "ok",
  "timestamp": "2026-03-13T06:00:00Z",
  "components": {
    "database": { "status": "ok", "event_count": 142, "latency_ms": 12 },
    "sqs_events_queue": { "status": "ok", "depth": 0 },
    "sqs_events_dlq": { "status": "ok", "depth": 0 },
    "sqs_social_queue": { "status": "ok", "depth": 3 }
  }
}
```
