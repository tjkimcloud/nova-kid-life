-- scraper_metrics: per-source quality scorecard.
-- Updated by the quality-agent Lambda after each scrape run.
-- Powers the feedback loop: low-scoring sources get flagged/disabled.

CREATE TABLE IF NOT EXISTS scraper_metrics (
    source_name         TEXT        PRIMARY KEY,
    -- Cumulative counters
    total_runs          INTEGER     NOT NULL DEFAULT 0,
    total_scraped       INTEGER     NOT NULL DEFAULT 0,
    total_published     INTEGER     NOT NULL DEFAULT 0,
    total_removed       INTEGER     NOT NULL DEFAULT 0,   -- failed quality filter
    consecutive_failures INTEGER    NOT NULL DEFAULT 0,
    -- Quality scores (rolling 4-week average)
    nova_relevance_score NUMERIC(4,3) DEFAULT NULL,       -- 0.0–1.0: how often events are actually NoVA
    avg_events_per_run  NUMERIC(6,1) DEFAULT NULL,
    -- Status
    status              TEXT        NOT NULL DEFAULT 'active',  -- active | flagged | disabled
    flag_reason         TEXT        DEFAULT NULL,
    -- Timestamps
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_run_at         TIMESTAMPTZ DEFAULT NULL,
    last_success_at     TIMESTAMPTZ DEFAULT NULL,
    last_flagged_at     TIMESTAMPTZ DEFAULT NULL
);

-- quality_filter_log: each event that was removed and why.
-- Gives us a corpus to tune the relevance filter over time.
CREATE TABLE IF NOT EXISTS quality_filter_log (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id        UUID        REFERENCES events(id) ON DELETE CASCADE,
    source_name     TEXT        NOT NULL,
    title           TEXT        NOT NULL,
    reason          TEXT        NOT NULL,   -- 'not_nova' | 'past_date' | 'duplicate' | 'low_quality'
    ai_score        NUMERIC(4,3) DEFAULT NULL,
    ai_reasoning    TEXT        DEFAULT NULL,
    filtered_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS quality_filter_log_source_idx ON quality_filter_log(source_name);
CREATE INDEX IF NOT EXISTS quality_filter_log_reason_idx ON quality_filter_log(reason);
