-- Newsletter subscriptions

create table newsletter_subs (
  id         uuid primary key default gen_random_uuid(),
  email      text not null unique,
  zip_code   text,
  frequency  text not null default 'weekly'
             check (frequency in ('daily', 'weekly')),
  is_active  boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger newsletter_subs_updated_at
  before update on newsletter_subs
  for each row execute function update_updated_at();

-- RLS: anyone can subscribe (insert); only service role can read/update/delete
alter table newsletter_subs enable row level security;

create policy "newsletter_subs_public_insert"
  on newsletter_subs for insert
  with check (true);
