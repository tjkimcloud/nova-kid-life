"""
Nova Orchestrator — weekly autoresearch loop for NovaKidLife.

Triggered by: EventBridge (Monday 8:00 AM EST)
              or manual: {"mode": "full"} | {"mode": "metrics_only"} | {"mode": "source_health"}

What it does:
1. Pulls metrics from GA4, GSC, and Supabase
2. Identifies which autoresearch loops to activate this week
3. Runs the Source Health loop (auto-disable dead sources)
4. Runs the Content loop (flag underperforming blog posts for rewrite)
5. Runs the Data Quality loop (aggregator URLs, missing descriptions)
6. Publishes a weekly digest to GitHub as an issue
7. Stores metric snapshots in SSM for trend tracking

Autoresearch loops (Karpathy-style: one editable target, one metric):
  - Source Loop:   editable=sources.json       metric=events_per_source_per_week
  - Content Loop:  editable=prompts.py hints   metric=GSC clicks per blog post
  - UX Loop:       editable=one component      metric=newsletter_subs weekly delta
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Any

import boto3
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ── Globals (filled by _load_secrets) ─────────────────────────────────────────

_SUPABASE_URL = ""
_SUPABASE_KEY = ""
_GITHUB_TOKEN = ""
_GITHUB_REPO  = "tjkimcloud/nova-kid-life"
_GA4_PROPERTY = ""
_GSC_PROPERTY = ""
_GOOGLE_SA    = {}   # service account dict

# ── Secret loading ─────────────────────────────────────────────────────────────

def _load_secrets() -> None:
    global _SUPABASE_URL, _SUPABASE_KEY, _GITHUB_TOKEN
    global _GA4_PROPERTY, _GSC_PROPERTY, _GOOGLE_SA

    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))

    def get(name: str, decrypt: bool = False) -> str:
        try:
            return ssm.get_parameter(Name=name, WithDecryption=decrypt)["Parameter"]["Value"]
        except Exception as e:
            logger.warning("SSM get %s failed: %s", name, e)
            return ""

    _SUPABASE_URL  = get("/novakidlife/supabase-url")
    _SUPABASE_KEY  = get("/novakidlife/supabase-service-key", decrypt=True)
    _GITHUB_TOKEN  = get("/novakidlife/github-token", decrypt=True)
    _GA4_PROPERTY  = get("/novakidlife/ga4-property-id")
    _GSC_PROPERTY  = get("/novakidlife/gsc-property")
    _GOOGLE_SA     = json.loads(get("/novakidlife/google-service-account", decrypt=True) or "{}")


_load_secrets()

# ── Supabase helpers ───────────────────────────────────────────────────────────

def _sb(method: str, path: str, **kwargs) -> Any:
    url = f"{_SUPABASE_URL}/rest/v1/{path}"
    headers = {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    r = httpx.request(method, url, headers=headers, timeout=20, **kwargs)
    r.raise_for_status()
    return r.json()

# ── Google credential helper ───────────────────────────────────────────────────

def _google_creds(scopes: list[str]):
    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_info(_GOOGLE_SA, scopes=scopes)

# ── Metric collectors ──────────────────────────────────────────────────────────

def collect_supabase_metrics() -> dict:
    """Pull key counts directly from Supabase."""
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()

    metrics = {}

    # Total published events
    r = _sb("GET", "events?select=id&status=eq.published", headers={"Range": "0-0", "Prefer": "count=exact"})
    # Use HEAD for count
    url = f"{_SUPABASE_URL}/rest/v1/events"
    headers = {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Prefer": "count=exact",
    }
    params = {"status": "eq.published", "select": "id"}
    resp = httpx.head(url, headers=headers, params=params, timeout=10)
    content_range = resp.headers.get("content-range", "0/0")
    metrics["total_published_events"] = int(content_range.split("/")[-1]) if "/" in content_range else 0

    # Newsletter subscribers
    resp = httpx.head(url.replace("/events", "/newsletter_subs"),
                      headers=headers, params={"select": "id"}, timeout=10)
    content_range = resp.headers.get("content-range", "0/0")
    metrics["newsletter_subs"] = int(content_range.split("/")[-1]) if "/" in content_range else 0

    # Events with aggregator registration URLs
    agg_domains = ["dullesmoms.com", "patch.com", "macaronikid.com", "mommypoppins.com"]
    agg_count = 0
    for domain in agg_domains:
        resp = httpx.head(url, headers=headers,
                          params={"status": "eq.published",
                                  "registration_url": f"ilike.%{domain}%",
                                  "select": "id"}, timeout=10)
        cr = resp.headers.get("content-range", "0/0")
        agg_count += int(cr.split("/")[-1]) if "/" in cr else 0
    metrics["events_with_aggregator_urls"] = agg_count

    # Events without images
    resp = httpx.head(url, headers=headers,
                      params={"status": "eq.published", "image_url": "is.null", "select": "id"},
                      timeout=10)
    cr = resp.headers.get("content-range", "0/0")
    metrics["events_without_images"] = int(cr.split("/")[-1]) if "/" in cr else 0

    # New events this week
    resp = httpx.head(url, headers=headers,
                      params={"created_at": f"gte.{week_ago}", "select": "id"},
                      timeout=10)
    cr = resp.headers.get("content-range", "0/0")
    metrics["new_events_this_week"] = int(cr.split("/")[-1]) if "/" in cr else 0

    return metrics


def collect_source_health() -> list[dict]:
    """Read scraper_metrics table — one row per source."""
    try:
        rows = _sb("GET", "scraper_metrics?select=source_name,status,nova_relevance_score,"
                          "avg_events_per_run,consecutive_failures&order=nova_relevance_score.asc")
        return rows if isinstance(rows, list) else []
    except Exception as e:
        logger.warning("scraper_metrics fetch failed: %s", e)
        return []


def collect_gsc_metrics(days: int = 28) -> list[dict]:
    """Pull top pages by clicks from Google Search Console."""
    if not _GOOGLE_SA:
        return []
    try:
        from googleapiclient.discovery import build
        creds = _google_creds(["https://www.googleapis.com/auth/webmasters.readonly"])
        gsc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
        end   = datetime.now(timezone.utc).date()
        start = end - timedelta(days=days)
        body  = {
            "startDate": start.isoformat(),
            "endDate":   end.isoformat(),
            "dimensions": ["page"],
            "rowLimit": 50,
            "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}],
        }
        resp = gsc.searchanalytics().query(siteUrl=_GSC_PROPERTY, body=body).execute()
        return resp.get("rows", [])
    except Exception as e:
        logger.warning("GSC fetch failed: %s", e)
        return []


def collect_ga4_metrics(days: int = 7) -> list[dict]:
    """Pull top pages by sessions from GA4."""
    if not _GOOGLE_SA or not _GA4_PROPERTY:
        return []
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Metric, Dimension
        )
        creds  = _google_creds(["https://www.googleapis.com/auth/analytics.readonly"])
        client = BetaAnalyticsDataClient(credentials=creds)
        req    = RunReportRequest(
            property=f"properties/{_GA4_PROPERTY}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="bounceRate"),
            ],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
            limit=50,
        )
        resp = client.run_report(req)
        rows = []
        for row in resp.rows:
            rows.append({
                "page":       row.dimension_values[0].value,
                "sessions":   int(row.metric_values[0].value),
                "users":      int(row.metric_values[1].value),
                "bounce_rate": float(row.metric_values[2].value),
            })
        return rows
    except Exception as e:
        logger.warning("GA4 fetch failed: %s", e)
        return []

# ── Source Health Loop ─────────────────────────────────────────────────────────

def run_source_health_loop(source_rows: list[dict]) -> dict:
    """
    Identify dead/failing sources.
    Returns a report — does NOT auto-modify sources.json (done via GitHub PR in orchestrator).
    """
    dead      = []   # consecutive_failures >= 5 OR avg_events_per_run < 1
    declining = []   # nova_relevance_score < 0.3
    healthy   = []

    for row in source_rows:
        name     = row.get("source_name", "unknown")
        score    = float(row.get("nova_relevance_score") or 0)
        avg_evts = float(row.get("avg_events_per_run") or 0)
        failures = int(row.get("consecutive_failures") or 0)
        status   = row.get("status", "active")

        if status == "disabled":
            continue
        if failures >= 5 or avg_evts < 1:
            dead.append({"source": name, "failures": failures, "avg_events": avg_evts})
        elif score < 0.3:
            declining.append({"source": name, "score": score})
        else:
            healthy.append(name)

    return {
        "dead_sources":      dead,
        "declining_sources": declining,
        "healthy_count":     len(healthy),
        "total_checked":     len(source_rows),
    }

# ── Content Loop ───────────────────────────────────────────────────────────────

def run_content_loop(gsc_rows: list[dict]) -> dict:
    """
    Identify blog posts with low CTR or low impressions vs. peers.
    Returns recommendations — no automated changes yet (loop matures after 4 weeks of data).
    """
    blog_rows = [r for r in gsc_rows if "/blog/" in r.get("keys", [""])[0]]

    if not blog_rows:
        return {"status": "no_data", "message": "GSC has no blog post data yet — check back in 2 weeks"}

    recommendations = []
    for row in blog_rows:
        page        = row["keys"][0]
        clicks      = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr         = row.get("ctr", 0)
        position    = row.get("position", 99)

        # High impressions, low CTR = title/description problem
        if impressions > 100 and ctr < 0.03:
            recommendations.append({
                "page": page, "issue": "high_impressions_low_ctr",
                "clicks": clicks, "impressions": impressions, "ctr": round(ctr, 4),
                "action": "Rewrite title and meta description — ranking well but not being clicked",
            })
        # Low impressions but ranking = content depth problem
        elif impressions < 20 and position < 30:
            recommendations.append({
                "page": page, "issue": "low_impressions_ranking",
                "position": round(position, 1),
                "action": "Expand content depth — ranking but Google not showing it widely",
            })

    return {
        "status": "ok",
        "blog_posts_analyzed": len(blog_rows),
        "recommendations": recommendations,
    }

# ── Metric snapshot ────────────────────────────────────────────────────────────

def save_metric_snapshot(metrics: dict) -> None:
    """Store this week's metrics in SSM for trend comparison next week."""
    try:
        ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        week = datetime.now(timezone.utc).strftime("%Y-W%W")
        ssm.put_parameter(
            Name=f"/novakidlife/metrics-snapshot/{week}",
            Value=json.dumps(metrics),
            Type="String",
            Overwrite=True,
        )
        logger.info("Metric snapshot saved for %s", week)
    except Exception as e:
        logger.warning("Metric snapshot save failed: %s", e)


def load_last_snapshot() -> dict:
    """Load last week's metric snapshot for delta calculation."""
    try:
        ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        last_week = (datetime.now(timezone.utc) - timedelta(weeks=1)).strftime("%Y-W%W")
        result = ssm.get_parameter(Name=f"/novakidlife/metrics-snapshot/{last_week}")
        return json.loads(result["Parameter"]["Value"])
    except Exception:
        return {}

# ── Weekly digest → GitHub issue ──────────────────────────────────────────────

def publish_digest(report: dict) -> str | None:
    """Open a GitHub issue with the weekly orchestrator report."""
    if not _GITHUB_TOKEN:
        logger.warning("No GitHub token — skipping digest")
        return None

    sb  = report.get("supabase", {})
    prev = report.get("prev_snapshot", {})

    def delta(key: str) -> str:
        cur  = sb.get(key, 0)
        last = prev.get(key, 0)
        if not last:
            return f"{cur}"
        diff = cur - last
        sign = "+" if diff >= 0 else ""
        return f"{cur} ({sign}{diff} vs last week)"

    source = report.get("source_health", {})
    content = report.get("content_loop", {})

    dead_list = "\n".join(
        f"  - `{s['source']}` — {s['failures']} consecutive failures, {s['avg_events']:.1f} avg events/run"
        for s in source.get("dead_sources", [])
    ) or "  None"

    rec_list = "\n".join(
        f"  - `{r['page']}` — {r['issue']}: {r['action']}"
        for r in content.get("recommendations", [])
    ) or "  None yet — GSC data still accumulating"

    body = f"""## NovaKidLife Weekly Orchestrator Report
*Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*

---

### Supabase Metrics

| Metric | Value |
|--------|-------|
| Published events | {delta('total_published_events')} |
| New events this week | {sb.get('new_events_this_week', 0)} |
| Newsletter subscribers | {delta('newsletter_subs')} |
| Events without images | {sb.get('events_without_images', 0)} |
| Events with aggregator URLs | {sb.get('events_with_aggregator_urls', 0)} |

---

### Source Health Loop

- **{source.get('healthy_count', 0)}** sources healthy
- **{len(source.get('dead_sources', []))}** sources flagged as dead (auto-disable candidates)
- **{len(source.get('declining_sources', []))}** sources declining in relevance score

**Dead sources (review for manual disable):**
{dead_list}

---

### Content Loop (GSC)

{content.get('message', '')}

**Recommendations:**
{rec_list}

---

### Next Actions

- [ ] Review dead sources above and confirm disable in `config/sources.json`
- [ ] Review content recommendations and trigger rewrite if agreed
- [ ] Check QA report at [GitHub Actions](https://github.com/{_GITHUB_REPO}/actions)

*This issue is auto-generated by the Nova Orchestrator. Close it when reviewed.*
"""

    # Check for existing open weekly digest
    headers = {
        "Authorization": f"token {_GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    existing = httpx.get(
        f"https://api.github.com/repos/{_GITHUB_REPO}/issues",
        headers=headers,
        params={"labels": "orchestrator-digest", "state": "open"},
        timeout=10,
    ).json()

    week_label = datetime.now(timezone.utc).strftime("Week of %b %d, %Y")
    title = f"Weekly Orchestrator Report — {week_label}"

    if existing and isinstance(existing, list) and existing:
        # Update existing
        issue_num = existing[0]["number"]
        httpx.patch(
            f"https://api.github.com/repos/{_GITHUB_REPO}/issues/{issue_num}",
            headers=headers, json={"body": body, "title": title}, timeout=10,
        )
        return f"https://github.com/{_GITHUB_REPO}/issues/{issue_num}"
    else:
        resp = httpx.post(
            f"https://api.github.com/repos/{_GITHUB_REPO}/issues",
            headers=headers,
            json={"title": title, "body": body, "labels": ["orchestrator-digest"]},
            timeout=10,
        )
        return resp.json().get("html_url")

# ── Lambda handler ─────────────────────────────────────────────────────────────

def handler(event: dict, context) -> dict:
    mode = event.get("mode", "full")
    logger.info("Orchestrator starting — mode=%s", mode)

    report: dict = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
    }

    # Always collect Supabase metrics
    logger.info("Collecting Supabase metrics...")
    report["supabase"] = collect_supabase_metrics()
    report["prev_snapshot"] = load_last_snapshot()

    if mode in ("full", "source_health"):
        logger.info("Running Source Health loop...")
        source_rows = collect_source_health()
        report["source_health"] = run_source_health_loop(source_rows)

    if mode in ("full", "metrics_only"):
        logger.info("Collecting GSC metrics...")
        gsc_rows = collect_gsc_metrics(days=28)
        report["gsc_top_pages"] = gsc_rows[:10]
        report["content_loop"] = run_content_loop(gsc_rows)

        logger.info("Collecting GA4 metrics...")
        report["ga4_top_pages"] = collect_ga4_metrics(days=7)

    # Save snapshot for next week's delta
    save_metric_snapshot(report["supabase"])

    # Publish digest to GitHub
    if mode == "full":
        logger.info("Publishing weekly digest...")
        issue_url = publish_digest(report)
        report["digest_url"] = issue_url
        logger.info("Digest published: %s", issue_url)

    logger.info("Orchestrator complete: %s", json.dumps({
        k: v for k, v in report.items()
        if k not in ("gsc_top_pages", "ga4_top_pages")
    }, default=str))

    return {"statusCode": 200, "body": report}
