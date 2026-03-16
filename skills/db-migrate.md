# Skill: Database Migrations (Supabase)

**Purpose:** Create and apply PostgreSQL migrations in Supabase.

## Prerequisites
- Supabase CLI installed: `npm install -g supabase`
- Project linked: `supabase link --project-ref <ref>`
- `SUPABASE_DB_URL` available in environment

## Create a New Migration

```bash
supabase migration new <descriptive_name>
# Example: supabase migration new add_events_table
```
This creates `supabase/migrations/<timestamp>_<name>.sql`. Write your SQL there.

## Migration File Conventions

```sql
-- Always wrap in a transaction
BEGIN;

-- Use IF NOT EXISTS / IF EXISTS to make migrations idempotent
CREATE TABLE IF NOT EXISTS events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT NOT NULL,
  description TEXT,
  start_at    TIMESTAMPTZ NOT NULL,
  end_at      TIMESTAMPTZ,
  location    TEXT,
  embedding   vector(1536),          -- pgvector for semantic search
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

-- Always add RLS
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

COMMIT;
```

## Apply Migrations

### Local (development)
```bash
supabase db push
```

### Production
```bash
# Dry run first — review the SQL that will execute
supabase db push --dry-run

# Apply
supabase db push
```

## Check Migration Status
```bash
supabase migration list
```

## Verify
```bash
supabase db inspect
# or connect directly:
psql "$SUPABASE_DB_URL" -c "\dt"
```

## Rollback
Supabase migrations are one-directional. To rollback:
1. Write a new migration that reverses the change
2. `supabase migration new rollback_<previous_name>`
3. Apply the rollback migration

## pgvector Setup
If pgvector is not enabled:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```
Run via Supabase Dashboard → SQL Editor, or add to an early migration.
