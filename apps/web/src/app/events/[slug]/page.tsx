import type { Metadata } from 'next'
import { getEvent } from '@/lib/api'
import type { Event } from '@/types/events'
import { extractCity } from '@/components/EventJsonLd'
import { EventDetailClient } from './EventDetailClient'

// ── Helpers (metadata only) ─────────────────────────────────────────────────────

function buildSeoTitle(event: Event): string {
  const city    = extractCity(event)
  const suffix  = ` — ${city}, VA`
  const maxTitle = 60 - suffix.length
  const title   = event.title.length > maxTitle
    ? event.title.slice(0, maxTitle - 1) + '…'
    : event.title
  return `${title}${suffix}`
}

function buildMetaDescription(event: Event): string {
  const d = new Date(event.start_at)
  const dateStr = d.toLocaleDateString('en-US', {
    weekday: 'short', month: 'short', day: 'numeric',
    timeZone: 'America/New_York',
  })
  const timeStr = d.toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit',
    timeZone: 'America/New_York',
  })
  const loc  = event.location_name || extractCity(event)
  const cost = event.is_free ? 'Free' : (event.cost_description ?? 'Paid admission')
  const snippet = event.description.replace(/\s+/g, ' ').trim().slice(0, 65)
  let desc = `${dateStr} · ${timeStr} at ${loc}. ${snippet}. ${cost}.`
  if (desc.length > 155) {
    desc = desc.slice(0, 154).replace(/\W+\S*$/, '') + '…'
  }
  return desc
}

// ── Static generation ──────────────────────────────────────────────────────────

// Only render slugs returned by generateStaticParams; 404 everything else.
// When the API is unavailable at build time, returns [] gracefully.
export const dynamicParams = false

export async function generateStaticParams() {
  try {
    const API = (process.env.NEXT_PUBLIC_API_URL ?? '').replace(/\/$/, '')
    const data = await fetch(`${API}/sitemap`, { cache: 'no-store' }).then((r) => r.json())
    // API returns { main_events: [{ slug, updated_at }, ...] }
    const items: Array<{ slug: string } | string> = data.main_events ?? data.main ?? []
    const slugs = items.map((item) => (typeof item === 'string' ? item : item.slug))
    if (slugs.length > 0) return slugs.map((slug) => ({ slug }))
  } catch {
    // API unavailable at build time — fall through to placeholder
  }
  // Next.js requires at least one entry for static export.
  // The placeholder slug hits notFound() in the page component.
  return [{ slug: '_placeholder' }]
}

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  try {
    const { slug } = await params
    const event = await getEvent(slug).catch(() => null)
    if (!event) return { title: 'Event Not Found | NovaKidLife' }
    const title       = buildSeoTitle(event)
    const description = buildMetaDescription(event)
    const pageUrl     = `https://novakidlife.com/events/${slug}`

    return {
      title,
      description,
      alternates: { canonical: pageUrl },
      openGraph: {
        title:       `${title} | NovaKidLife`,
        description,
        type:        'article',
        ...(event.og_image_url && {
          images: [{
            url:    event.og_image_url,
            width:  1200,
            height: 630,
            alt:    event.image_alt ?? event.title,
          }],
        }),
      },
      twitter: { card: 'summary_large_image' },
    }
  } catch {
    return { title: 'Event — Northern Virginia | NovaKidLife' }
  }
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default async function EventDetailPage(
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params
  // Content is loaded client-side by EventDetailClient to avoid build-time
  // API timeouts that caused all event pages to bake in "Page not found".
  return <EventDetailClient slug={slug} />
}
