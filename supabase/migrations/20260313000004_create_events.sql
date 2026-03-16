-- Core events table — the heart of NovaKidLife

create table events (
  -- Identity
  id               uuid primary key default gen_random_uuid(),
  slug             text not null unique,

  -- Content (AI-enriched)
  title            text not null,
  short_description text,
  full_description  text,
  seo_title        text,
  seo_description  text,
  age_range        text,             -- human-readable e.g. "3–8 years"
  age_min          int,              -- for filtering
  age_max          int,              -- for filtering
  tags             text[] not null default '{}',
  is_free          boolean not null default false,
  cost_description text,             -- e.g. "$5/person, under 2 free"

  -- Media
  image_url        text,             -- CloudFront URL to AI-generated webp

  -- Location
  location_text    text,             -- human-readable e.g. "Reston, VA"
  location_id      uuid references locations(id) on delete set null,
  lat              double precision,
  lng              double precision,
  venue_name       text,
  address          text,

  -- Timing
  start_at         timestamptz not null,
  end_at           timestamptz,
  is_recurring     boolean not null default false,
  recurrence_rule  text,             -- iCal RRULE if recurring

  -- Source
  source_url       text not null unique,   -- deduplication key
  source_name      text,                   -- e.g. "fairfax-parks"
  registration_url text,

  -- Classification
  category_id      uuid references categories(id) on delete set null,

  -- Pipeline status
  -- raw → scraped but not yet enriched
  -- enriched → AI content generated, image pending
  -- published → fully ready, visible to users
  -- archived → past events or manually hidden
  status           text not null default 'raw'
                   check (status in ('raw', 'enriched', 'published', 'archived')),

  -- Flags
  is_featured      boolean not null default false,
  is_published     boolean not null default false,  -- convenience alias for status = published

  -- AI semantic search
  embedding        extensions.vector(1536),  -- OpenAI text-embedding-3-small dimensions

  -- Audit
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

-- Auto-update updated_at on any row change
-- security definer + fixed search_path prevents search_path manipulation
create or replace function public.update_updated_at()
returns trigger language plpgsql
security definer
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger events_updated_at
  before update on events
  for each row execute function update_updated_at();

-- RLS: public can read published events only; service role handles writes
alter table events enable row level security;

create policy "events_public_read"
  on events for select
  using (status = 'published');

-- Performance indexes
create index events_start_at_idx       on events (start_at);
create index events_status_idx         on events (status);
create index events_category_id_idx    on events (category_id);
create index events_location_id_idx    on events (location_id);
create index events_is_featured_idx    on events (is_featured) where is_featured = true;
create index events_is_free_idx        on events (is_free) where is_free = true;
create index events_tags_idx           on events using gin (tags);
create index events_age_range_idx      on events (age_min, age_max);

-- Geo index for radius queries
create index events_geo_idx            on events (lat, lng)
  where lat is not null and lng is not null;

-- pgvector index for semantic search (IVFFlat, tune lists when > 1000 rows)
create index events_embedding_idx      on events
  using ivfflat (embedding extensions.vector_cosine_ops)
  with (lists = 100);
