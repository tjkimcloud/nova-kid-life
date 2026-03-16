-- Add section field to events table.
-- Enables separate site sections (main events feed vs pokemon hub vs future hobby sections).
-- Default 'main' means all existing events are unaffected.

alter table events
  add column if not exists section text not null default 'main';

-- Index for fast section-filtered queries (e.g. all pokemon events by date)
create index if not exists events_section_idx
  on events (section, start_at desc);

-- Comment documents valid values
comment on column events.section is
  'Site section this event belongs to. Values: main | pokemon. Extend as new sections are added.';
