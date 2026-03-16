-- Extend events table to support deals and promotions alongside family events.
-- event_type distinguishes between calendar events, restaurant deals, birthday
-- freebies, amusement park offers, and other family-value content.

alter table events
  add column if not exists event_type text not null default 'event'
    check (event_type in ('event', 'deal', 'birthday_freebie', 'amusement', 'seasonal')),
  add column if not exists brand text,              -- e.g. "Chipotle", "Shake Shack"
  add column if not exists discount_description text, -- e.g. "BOGO entrée with purchase"
  add column if not exists deal_category text
    check (deal_category in ('restaurant', 'activity', 'amusement', 'grocery', 'seasonal', null));

-- Index for deal queries
create index events_event_type_idx on events (event_type);
create index events_brand_idx      on events (brand) where brand is not null;
