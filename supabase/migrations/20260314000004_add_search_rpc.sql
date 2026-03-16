-- RPC function for pgvector semantic search.
-- Called by POST /events/search in the API Lambda.
-- Returns events ordered by cosine similarity to the query embedding.

create or replace function search_events(
  query_embedding extensions.vector(1536),
  match_section   text    default 'main',
  match_count     int     default 10
)
returns table (
  id               uuid,
  slug             text,
  title            text,
  description      text,
  start_at         timestamptz,
  location_name    text,
  event_type       text,
  section          text,
  tags             text[],
  is_free          boolean,
  image_url        text,
  image_url_sm     text,
  image_alt        text,
  image_blurhash   text,
  image_width      int,
  image_height     int,
  similarity       float
)
language sql stable
security definer
set search_path = ''
as $$
  select
    e.id,
    e.slug,
    e.title,
    e.full_description  as description,
    e.start_at,
    e.venue_name        as location_name,
    e.event_type,
    e.section,
    e.tags,
    e.is_free,
    e.image_url,
    e.image_url_sm,
    e.image_alt,
    e.image_blurhash,
    e.image_width,
    e.image_height,
    1 - (e.embedding OPERATOR(extensions.<=>) query_embedding) as similarity
  from public.events e
  where
    e.status  = 'published'
    and e.section = match_section
    and e.embedding is not null
  order by e.embedding OPERATOR(extensions.<=>) query_embedding
  limit match_count;
$$;

-- Grant execute to the service role (used by API Lambda)
grant execute on function search_events(extensions.vector, text, int)
  to service_role;
