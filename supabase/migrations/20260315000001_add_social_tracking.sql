-- Track which social platforms each event has been posted to.
-- Prevents duplicate posts when the social-poster Lambda runs multiple times.

alter table events
  add column if not exists social_posted_platforms text[] not null default '{}',
  add column if not exists social_posted_at         timestamptz;

comment on column events.social_posted_platforms is
  'Platforms this event has been posted to. Values: twitter | instagram | facebook';
comment on column events.social_posted_at is
  'Timestamp of first social post for this event';

create index if not exists events_social_posted_idx
  on events using gin (social_posted_platforms)
  where status = 'published';
