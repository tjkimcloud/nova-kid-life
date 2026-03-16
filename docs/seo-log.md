# SEO Implementation Log — NovaKidLife

Target: Rank #1 for "family events Northern Virginia", "kids activities NoVa", and long-tail event queries.

Legend: ✅ Done | 🔄 In Progress | ⬜ Not Started

---

## Technical SEO Foundation

### Metadata (Next.js Metadata API)
- ✅ Default `title` and `title.template` in root `layout.tsx`
- ✅ Default `description` in root `layout.tsx`
- ✅ `metadataBase` set to `https://novakidlife.com`
- ✅ OpenGraph: `siteName`, `locale`, `type`
- ✅ Twitter card: `summary_large_image`
- ✅ `robots: { index: true, follow: true }`
- ⬜ Per-page `title` and `description` (Session 6-7)
- ⬜ Per-event OG image (Session 7)
- ⬜ Per-event Twitter image (Session 7)

### Sitemaps
- ⬜ `sitemap.ts` using Next.js metadata API (Session 11)
- ⬜ Static pages included (home, /events, /categories)
- ⬜ All event slugs included (fetched from API at build time)
- ⬜ `lastModified` from `updated_at`
- ⬜ Priority and `changeFrequency` tuned per page type
- ⬜ Submitted to Google Search Console

### Robots
- ⬜ `robots.ts` using Next.js metadata API (Session 11)
- ⬜ Allow all crawlers
- ⬜ Disallow `/admin/`
- ⬜ Reference sitemap URL

### Canonical URLs
- ⬜ `alternates.canonical` set on all pages (Session 6-7)
- ⬜ No duplicate content from query params (filter state in URL must be canonical-safe)

### Core Web Vitals (Lighthouse Targets)
- ⬜ Performance ≥ 90 (Session 11)
- ⬜ Accessibility ≥ 95 (Session 11)
- ⬜ Best Practices ≥ 90 (Session 11)
- ⬜ SEO ≥ 95 (Session 11)
- ⬜ LCP < 2.5s
- ⬜ CLS < 0.1
- ⬜ TBT < 300ms
- ⬜ FCP < 1.8s

---

## Structured Data (JSON-LD)

### Event Schema (per event page)
- ⬜ `@type: "Event"` (Session 7)
- ⬜ `name`, `description`, `startDate`, `endDate`
- ⬜ `location` with `@type: "Place"`, `name`, `address`
- ⬜ `image` array
- ⬜ `organizer`
- ⬜ `offers` (free/paid, price, url)
- ⬜ `eventStatus: "EventScheduled"`
- ⬜ `eventAttendanceMode: "OfflineEventAttendanceMode"`
- ⬜ Test with Google Rich Results Test

### LocalBusiness Schema (home page)
- ⬜ `@type: "LocalBusiness"` (Session 11)
- ⬜ `name: "NovaKidLife"`
- ⬜ `description`, `url`, `logo`
- ⬜ `areaServed: "Northern Virginia"`

### BreadcrumbList Schema (event pages)
- ⬜ Home → Events → Event Title (Session 7)

---

## On-Page SEO

### Home Page
- ⬜ H1 targeting primary keyword (Session 6)
- ⬜ Location-specific copy ("Northern Virginia", county names)
- ⬜ Internal links to category and location pages

### Events Listing Page (`/events`)
- ⬜ Unique title: "Family Events in Northern Virginia | NovaKidLife"
- ⬜ Unique description targeting browse intent
- ⬜ H1 with keyword
- ⬜ Category filter links (pass PageRank to category pages)

### Event Detail Pages (`/events/[slug]`)
- ⬜ AI-generated `seo_title` used as page `<title>` (max 60 chars)
- ⬜ AI-generated `seo_description` used as meta description (max 155 chars)
- ⬜ H1 = event title
- ⬜ Location in copy (signals local relevance)
- ⬜ Date in copy (signals freshness)

### Category Pages (future)
- ⬜ `/events/outdoor`, `/events/free`, etc. (Session 6 stretch)

### Location Pages (future)
- ⬜ `/events/fairfax`, `/events/arlington`, etc.

---

## Off-Page SEO

### Google Search Console
- ⬜ Property verified (Session 12)
- ⬜ Sitemap submitted
- ⬜ Core Web Vitals report reviewed
- ⬜ Coverage errors resolved

### Google Business Profile
- ⬜ NovaKidLife listing created (Session 12)
- ⬜ Category: "Family Entertainment Center" or "Event Planner"
- ⬜ Website URL set
- ⬜ Description written

### Backlink Strategy (ongoing)
- ⬜ NoVa parenting Facebook groups — share individual events
- ⬜ Reach out to Fairfax County Parks for listing partnership
- ⬜ NOVA family blogs / influencers outreach
- ⬜ Local news / Patch.com — submit press release for launch

---

## SEO Monitoring

- ⬜ Google Search Console impressions/clicks tracked weekly
- ⬜ Ahrefs / SEMrush rank tracking for target keywords
- ⬜ Core Web Vitals tracked via Search Console field data
- ⬜ Lighthouse CI in GitHub Actions catches regressions

### Target Keywords (primary)
1. "family events northern virginia"
2. "things to do with kids nova"
3. "kids activities fairfax county"
4. "free family events northern virginia"
5. "weekend activities for kids nova"

### Target Keywords (long-tail, event-level)
- "[event name] [city] [year]"
- "[activity type] for kids [city]"
- "things to do in [city] with toddlers"
