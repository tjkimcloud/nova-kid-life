-- Migration: fix blog_posts upsert constraint
--
-- The original migration created a functional unique index using COALESCE:
--   CREATE UNIQUE INDEX ... ON blog_posts (post_type, COALESCE(area, 'nova'), date_range_start)
--
-- Postgres ON CONFLICT requires a plain unique constraint or index on column
-- expressions, not a functional index with COALESCE. This caused error 42P10:
--   "there is no unique or exclusion constraint matching the ON CONFLICT specification"
--
-- Fix: drop the functional index, add a plain unique constraint.
-- The content-generator always sets area explicitly ('nova', 'fairfax', etc.)
-- so NULL area is not a practical case.

DROP INDEX IF EXISTS public.blog_posts_type_area_date_idx;

ALTER TABLE public.blog_posts
    ADD CONSTRAINT blog_posts_type_area_date_key
    UNIQUE (post_type, area, date_range_start);
