-- Clean up registration_url values that point to aggregator/calendar sites
-- rather than the event organizer's own website.
--
-- These were stored before publisher.py gained _AGGREGATOR_DOMAINS filtering.
-- After this migration, registration_url will only contain real organizer URLs.
-- New events scraped going forward are already filtered by publisher.py.

UPDATE events
SET registration_url = NULL
WHERE registration_url IS NOT NULL
  AND (
    -- Calendar aggregators
    registration_url ILIKE '%dullesmoms.com%'
    OR registration_url ILIKE '%patch.com%'
    OR registration_url ILIKE '%macaronikid.com%'
    OR registration_url ILIKE '%mommypoppins.com%'
    OR registration_url ILIKE '%dc.kidsoutandabout.com%'
    OR registration_url ILIKE '%kidsoutandabout.com%'
    OR registration_url ILIKE '%kidfriendlydc.com%'
    OR registration_url ILIKE '%thingstodoindc.com%'
    OR registration_url ILIKE '%bringthekids.com%'
    -- Local news / blogs
    OR registration_url ILIKE '%restonow.com%'
    OR registration_url ILIKE '%arlnow.com%'
    OR registration_url ILIKE '%ffxnow.com%'
    OR registration_url ILIKE '%loudounnow.com%'
    OR registration_url ILIKE '%insidenova.com%'
    OR registration_url ILIKE '%alxnow.com%'
    OR registration_url ILIKE '%tysonsreporter.com%'
    OR registration_url ILIKE '%princewilliamtimes.com%'
    OR registration_url ILIKE '%potomaclocal.com%'
    OR registration_url ILIKE '%novatoday.6amcity.com%'
    -- Parenting sites
    OR registration_url ILIKE '%theloudounmoms.com%'
    OR registration_url ILIKE '%northernvirginiamag.com%'
    OR registration_url ILIKE '%funinfairfaxva.com%'
    OR registration_url ILIKE '%novamomsblog.com%'
    OR registration_url ILIKE '%fairfaxfamilyfun.com%'
    -- Tourism boards
    OR registration_url ILIKE '%visitfairfax.org%'
    OR registration_url ILIKE '%visitloudoun.org%'
    OR registration_url ILIKE '%visitalexandriava.com%'
    OR registration_url ILIKE '%visitarlington.com%'
  );
