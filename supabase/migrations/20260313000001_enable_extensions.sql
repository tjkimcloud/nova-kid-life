-- Dedicated schema for extensions (Supabase security best practice)
create schema if not exists extensions;

-- Enable pgvector for semantic search (AI embeddings)
create extension if not exists vector schema extensions;

-- Enable uuid generation
create extension if not exists "uuid-ossp" schema extensions;

-- Make extension types available to public schema without prefix
grant usage on schema extensions to postgres, anon, authenticated, service_role;
