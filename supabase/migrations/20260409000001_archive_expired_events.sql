-- Archive events that have definitively expired (explicit end_at in the past).
-- This covers seasonal deals (Easter, holiday), food promotions, and any
-- event with a hard end date that has already passed.
-- Safe/reversible: only changes status, does not delete rows.

UPDATE events
SET status = 'archived'
WHERE status = 'published'
  AND end_at IS NOT NULL
  AND end_at < NOW();

-- Also archive deal/seasonal events with a start_at older than 45 days
-- and no end_at — these are stale promotions that were never given an
-- expiry date (e.g. old Easter content, expired restaurant promotions).
UPDATE events
SET status = 'archived'
WHERE status = 'published'
  AND event_type IN ('deal', 'seasonal', 'product_drop')
  AND end_at IS NULL
  AND start_at < NOW() - INTERVAL '45 days';
