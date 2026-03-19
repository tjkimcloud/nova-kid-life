---
name: next-15-patterns
description: Next.js 15 static export patterns and gotchas for NovaKidLife — generateStaticParams, params Promise type, notFound() placement, force-static, client component rules, Suspense boundaries, TypeScript error table, runtime issues, and required build-time environment variables. Reference file for writing correct App Router code.
triggers:
  - generateStaticParams
  - params Promise
  - notFound
  - force-static
  - static export
  - useSearchParams
  - Next.js 15
  - App Router
  - TypeScript error
---

# Skill: Next.js 15 Static Export Patterns

**Reference:** Use when writing or reviewing App Router pages for `output: 'export'`.
For the build checklist, see `qa-build.md`.

---

## 1. Dynamic Route — `generateStaticParams` Required

**Error:** `Page "/path/[slug]" is missing "generateStaticParams()"`

Every `[slug]` route MUST export `generateStaticParams`. Never return an empty array — Next.js 15 rejects it.

```tsx
export const dynamicParams = false  // required alongside generateStaticParams

export async function generateStaticParams() {
  try {
    const data = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/sitemap`,
      { signal: AbortSignal.timeout(8000) }   // prevent build hang if API is offline
    ).then(r => r.json())
    const slugs = data.slugs ?? []
    if (slugs.length > 0) return slugs.map((slug: string) => ({ slug }))
  } catch { /* API unavailable at build time */ }
  // Must return at least 1 entry — empty array is rejected by Next.js 15
  return [{ slug: '_placeholder' }]
}
```

---

## 2. `notFound()` Inside `try/catch` — Swallowed

**Error:** Page renders blank or throws unexpected error instead of 404.

`notFound()` throws a special Next.js error. If it's inside a catch block, the same catch swallows it.

**Wrong:**
```tsx
try {
  event = await getEvent(slug)
} catch {
  notFound()  // ← caught by the same catch
}
```

**Correct:**
```tsx
const event = await getEvent(slug).catch(() => null)
if (!event) notFound()  // ← outside try/catch, propagates correctly
```

---

## 3. `params` Is a Promise in Next.js 15

**Error:** `Type '{ params: { slug: string } }' does not satisfy constraint 'PageProps'`

```tsx
// generateMetadata
export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  const { slug } = await params
  // ...
}

// Page component
export default async function Page(
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params
  // ...
}
```

---

## 4. Metadata Routes Need `force-static`

**Error:** `export const dynamic = "force-static" not configured on route "/robots.txt"`

Any file using Next.js metadata API conventions (`robots.ts`, `sitemap.ts`, `opengraph-image.tsx`) must export `dynamic = 'force-static'`.

```ts
export const dynamic = 'force-static'

export default function robots() { ... }
```

---

## 5. `async headers()` Not Supported in Static Export

**Warning:** `Specified "headers" will not automatically work with "output: export"`

Remove `async headers()` from `next.config.js`. Set all cache/security headers as CloudFront response headers policies in Terraform.

---

## 6. Forms Must Be Client Components

HTML `<form>` with `onSubmit`, `useState`, or any interactivity must be `'use client'`.
Do NOT use `action="/api/..."` — there is no API server in static export. POST to `NEXT_PUBLIC_API_URL` from a client component.

---

## 7. `useSearchParams` Requires Suspense Boundary

**Error:** `useSearchParams() should be wrapped in a suspense boundary`

Wrap any `'use client'` component using `useSearchParams` in `<Suspense>` from its parent server component.

```tsx
// page.tsx (server component)
export default function EventsPage() {
  return (
    <Suspense fallback={<EventGridSkeleton />}>
      <EventsClient />    {/* 'use client' — uses useSearchParams */}
    </Suspense>
  )
}
```

---

## TypeScript Error Quick Reference

| Error | Fix |
|-------|-----|
| `Property 'x' does not exist on type 'never'` | `notFound()` return type is `never` — check control flow above |
| `Type 'null' is not assignable to type 'Event'` | Use `.catch(() => null)` + null guard |
| `Object is possibly 'null'` | Add null check or `!` if you're certain |
| `Cannot find module '@/...'` | Check `tsconfig.json` path alias and file exists |
| `'use client'` directive error | Move hooks to a `'use client'` file |
| `params` type error | Wrap in `Promise<{...}>` and await (see #3 above) |

---

## Runtime Issues (won't fail build — break UX)

| Issue | Location | Fix |
|-------|----------|-----|
| Broken links to unbuilt pages | Any `<Link href="/pokemon/drops">` | Build the target page or remove the link |
| API URL hardcoded to localhost | `.env.local` | Set `NEXT_PUBLIC_API_URL` to production URL before deploy |
| Missing OG image fallback | Event pages with no `og_image_url` | Ensure image pipeline runs before pages are indexed |
| Newsletter form posting to wrong URL | `NewsletterForm.tsx` | Verify `NEXT_PUBLIC_API_URL` set at build time |
| Stale sitemap at build time | `sitemap.ts` | API must be running during production build |

---

## Environment Variables Required at Build Time

Any `NEXT_PUBLIC_` variable not set at build time becomes `undefined` in the bundle — silently breaks features.

| Variable | Used for | Required at build? |
|----------|----------|--------------------|
| `NEXT_PUBLIC_API_URL` | API calls, newsletter form | Yes — baked into JS bundle |
| `NEXT_PUBLIC_SITE_URL` | Canonical URLs, sitemap | Yes |
| `NEXT_PUBLIC_SUPABASE_URL` | If used client-side | Yes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | If used client-side | Yes |
