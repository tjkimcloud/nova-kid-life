-- scraper_source_cache: persists per-source content hashes so the scraper
-- can skip GPT extraction when a page hasn't changed since the last run.
--
-- The events-scraper Lambda reads all rows at startup (one query),
-- checks hashes locally in memory, then bulk-upserts updates at the end.

CREATE TABLE IF NOT EXISTS scraper_source_cache (
    source_name     TEXT        PRIMARY KEY,
    content_hash    TEXT        NOT NULL,
    last_scraped_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    events_found    INTEGER     NOT NULL DEFAULT 0
);

-- No RLS — only accessed via service role key from Lambda
