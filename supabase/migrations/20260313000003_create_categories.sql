-- Event categories taxonomy

create table categories (
  id         uuid primary key default gen_random_uuid(),
  slug       text not null unique,
  name       text not null,
  icon       text,                    -- emoji icon for UI
  sort_order int  not null default 0,
  created_at timestamptz not null default now()
);

-- RLS: public read, no public write
alter table categories enable row level security;

create policy "categories_public_read"
  on categories for select
  using (true);

-- Seed core categories
insert into categories (slug, name, icon, sort_order) values
  ('outdoor',        'Outdoor',           '🌳', 1),
  ('arts-crafts',    'Arts & Crafts',     '🎨', 2),
  ('sports',         'Sports & Fitness',  '⚽', 3),
  ('educational',    'Educational',       '📚', 4),
  ('music',          'Music & Dance',     '🎵', 5),
  ('nature',         'Nature & Science',  '🔬', 6),
  ('food',           'Food & Cooking',    '🍕', 7),
  ('holiday',        'Holiday & Seasonal','🎉', 8),
  ('free',           'Free Events',       '🆓', 9),
  ('playdate',       'Playdates',         '🧸', 10),
  ('theater',        'Theater & Shows',   '🎭', 11),
  ('swimming',       'Swimming & Water',  '🏊', 12),
  ('library',        'Library Programs',  '📖', 13),
  ('community',      'Community Events',  '🏘️', 14),
  ('camps',          'Camps & Programs',  '⛺', 15);
