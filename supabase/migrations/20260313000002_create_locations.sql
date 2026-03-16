-- Northern Virginia locations reference table
-- Seeded with counties and key cities — used for filtering and SEO location pages

create table locations (
  id         uuid primary key default gen_random_uuid(),
  slug       text not null unique,
  name       text not null,
  type       text not null check (type in ('county', 'city', 'region')),
  county     text,                    -- parent county for city-type rows
  lat        double precision,
  lng        double precision,
  sort_order int  not null default 0,
  created_at timestamptz not null default now()
);

-- RLS: public read, no public write
alter table locations enable row level security;

create policy "locations_public_read"
  on locations for select
  using (true);

-- Seed core NoVa locations
insert into locations (slug, name, type, lat, lng, sort_order) values
  ('northern-virginia', 'Northern Virginia',  'region', 38.8048, -77.0469, 0),
  ('fairfax-county',   'Fairfax County',      'county', 38.8462, -77.3064, 1),
  ('arlington',        'Arlington County',    'county', 38.8816, -77.0910, 2),
  ('loudoun-county',   'Loudoun County',      'county', 39.0840, -77.6541, 3),
  ('prince-william',   'Prince William County','county',38.6985, -77.5547, 4),
  ('alexandria',       'Alexandria',          'city',   38.8048, -77.0469, 5),
  ('reston',           'Reston',              'city',   38.9687, -77.3411, 6),
  ('herndon',          'Herndon',             'city',   38.9696, -77.3861, 7),
  ('mclean',           'McLean',              'city',   38.9340, -77.1773, 8),
  ('vienna',           'Vienna',              'city',   38.9012, -77.2653, 9),
  ('ashburn',          'Ashburn',             'city',   39.0437, -77.4875, 10),
  ('leesburg',         'Leesburg',            'city',   39.1157, -77.5636, 11),
  ('sterling',         'Sterling',            'city',   39.0026, -77.4088, 12),
  ('woodbridge',       'Woodbridge',          'city',   38.6590, -77.2497, 13),
  ('manassas',         'Manassas',            'city',   38.7509, -77.4753, 14);

-- counties column for cities
update locations set county = 'fairfax-county' where slug in ('reston','herndon','mclean','vienna');
update locations set county = 'loudoun-county' where slug in ('ashburn','leesburg','sterling');
update locations set county = 'prince-william' where slug in ('woodbridge','manassas');
