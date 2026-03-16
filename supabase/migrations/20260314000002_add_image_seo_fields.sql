-- Add image SEO fields to events table.
-- Stores all variants + metadata needed for Core Web Vitals and structured data.

alter table events
  add column if not exists image_alt        text,          -- AI-generated alt text (SEO + a11y)
  add column if not exists image_width      int,           -- prevents CLS (always 1200)
  add column if not exists image_height     int,           -- prevents CLS (always 675)
  add column if not exists image_blurhash   text,          -- base64 LQIP data URL for blur-up
  add column if not exists image_url_md     text,          -- 800×450 srcset medium
  add column if not exists image_url_sm     text,          -- 400×225 srcset small
  add column if not exists social_image_url text,          -- 1080×1080 illustration for social posts
  add column if not exists og_image_url     text;          -- 1200×630 for OpenGraph / Twitter card
