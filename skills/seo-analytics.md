---
name: seo-analytics
description: Analytics and measurement setup for NovaKidLife — Google Search Console tracking items, GA4 key events with parameters, KPI table with month 3 and month 6 targets, and SEO health monitoring for CloudWatch. Activates during infra and monitoring sessions.
triggers:
  - analytics
  - Google Search Console
  - GA4
  - KPI
  - tracking
  - Lighthouse
  - CloudWatch
  - metrics
---

# Skill: SEO Analytics & Measurement

**Activation:** Apply during infra sessions, monitoring sessions, and when setting up tracking. Not a content session skill.

---

## 1. Google Search Console (free, essential)

Set up at launch. Track weekly:

- **Index coverage** — are event pages being indexed?
- **Search queries** — what are people actually searching to find us?
- **Click-through rates by page** — which titles/descriptions underperform? (Fix in `seo-technical.md`)
- **Core Web Vitals report** — field data from real users (targets in `seo-technical.md` section 8)
- **Rich results** — are Event schema rich results appearing? (Schema in `seo-schema.md`)

Submit sitemap at launch:
- Google Search Console → Sitemaps → Submit `https://novakidlife.com/sitemap.xml`
- Bing Webmaster Tools → same (critical for ChatGPT + Copilot AI citation)

---

## 2. Google Analytics 4 Key Events

Track from day 1 with these event names and parameters:

| Event name | When to fire | Key parameters |
|-----------|-------------|----------------|
| `event_page_view` | Event detail page load | `event_slug`, `section`, `event_type` |
| `filter_applied` | Any filter change on /events | `filter_type`, `filter_value` |
| `search_performed` | Search submitted | `query_text`, `results_count` |
| `register_click` | Click on registration link | `event_slug`, `registration_url` |
| `share_click` | Click any share button | `event_slug`, `platform` |
| `newsletter_subscribe` | Newsletter form submit | (none required) |

---

## 3. KPI Targets

| KPI | Target (month 3) | Target (month 6) |
|-----|-----------------|-----------------|
| Organic sessions/month | 500 | 5,000 |
| Indexed pages | 100+ | 500+ |
| GBP impressions/month | 200 | 1,000 |
| Email subscribers | 50 | 500 |
| Event detail avg. time on page | > 45s | > 60s |
| Lighthouse score (all pages) | 90+ | 95+ |

---

## 4. SEO Health Monitoring — CloudWatch Alarms

Add these to the monitoring stack (Session 12 infra):

| Alert | Trigger | Action |
|-------|---------|--------|
| Broken link spike | 404 rate > 2% of requests in 1h | Investigate + fix redirect |
| Sitemap staleness | No sitemap rebuild in 48h | Check deploy pipeline |
| Search Console coverage errors | New crawl errors appear | Fix canonical or redirect |
| Lighthouse regression | Score drops below 85 on any category | PR blocked until fixed |

---

## 5. Reporting Cadence

- **Weekly (5 min):** GSC clicks + impressions, top queries, any new coverage errors
- **Monthly (30 min):** Full KPI review vs. targets, rank tracking (cross-reference `local-seo-tracking.md`), citation audit
- **Quarterly:** Full Lighthouse audit, E-E-A-T review, competitive gap analysis
