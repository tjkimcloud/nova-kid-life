-- Replace the overly permissive newsletter INSERT policy with one that
-- validates email format. This satisfies the Supabase security linter
-- while still allowing public subscriptions.

drop policy if exists "newsletter_subs_public_insert" on newsletter_subs;

create policy "newsletter_subs_public_insert"
  on newsletter_subs for insert
  with check (
    email ~* '^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'
  );
