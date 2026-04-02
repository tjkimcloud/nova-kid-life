import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getBlogPost, getBlogPosts } from '@/lib/api'
import { EventCard } from '@/components/EventCard'
import { AREA_LABELS, POST_TYPE_LABELS } from '@/types/blog'
import type { BlogPostWithEvents } from '@/types/blog'
import type { Event } from '@/types/events'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://novakidlife.com'

// ── Static params ──────────────────────────────────────────────────────────────

export async function generateStaticParams() {
  try {
    const data = await getBlogPosts({ limit: 100 })
    const slugs = data.items.map(p => ({ slug: p.slug }))
    return slugs.length > 0 ? slugs : [{ slug: '_placeholder' }]
  } catch {
    return [{ slug: '_placeholder' }]
  }
}

// ── Metadata ───────────────────────────────────────────────────────────────────

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  try {
    const { slug } = await params
    const post = await getBlogPost(slug)
    return {
      title:       post.title,
      description: post.meta_description ?? undefined,
      openGraph: {
        title:       `${post.title} | NovaKidLife`,
        description: post.meta_description ?? undefined,
        type:        'article',
        url:         `${SITE_URL}/blog/${post.slug}`,
        publishedTime: post.published_at,
      },
      alternates: {
        canonical: `${SITE_URL}/blog/${post.slug}`,
      },
    }
  } catch {
    return { title: 'Weekend Guide | NovaKidLife' }
  }
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  let post: BlogPostWithEvents

  try {
    post = await getBlogPost(slug)
  } catch {
    notFound()
  }

  const dateRange = formatDateRange(post.date_range_start, post.date_range_end)
  const canonical = `${SITE_URL}/blog/${post.slug}`

  // JSON-LD schemas
  const articleSchema = {
    '@context':       'https://schema.org',
    '@type':          'Article',
    headline:         post.title,
    description:      post.meta_description,
    url:              canonical,
    datePublished:    post.published_at,
    dateModified:     post.published_at,
    author: {
      '@type': 'Organization',
      name:    'NovaKidLife',
      url:     SITE_URL,
    },
    publisher: {
      '@type': 'Organization',
      name:    'NovaKidLife',
      url:     SITE_URL,
    },
    mainEntityOfPage: canonical,
    areaServed: {
      '@type': 'State',
      name:    'Virginia',
    },
  }

  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type':    'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home',           item: SITE_URL },
      { '@type': 'ListItem', position: 2, name: 'Weekend Guides', item: `${SITE_URL}/blog` },
      { '@type': 'ListItem', position: 3, name: post.title,       item: canonical },
    ],
  }

  // Event schemas (nested — one per event in the post)
  const eventSchemas = post.events.map(e => ({
    '@context': 'https://schema.org',
    '@type':    'Event',
    name:        e.title,
    startDate:   e.start_at,
    location: {
      '@type': 'Place',
      name:     e.venue_name,
      address:  e.location_text ?? undefined,
    },
    isAccessibleForFree: e.is_free,
    url: `${SITE_URL}/events/${e.slug}`,
  }))

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }} />
      {eventSchemas.map((s, i) => (
        <script key={i} type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(s) }} />
      ))}

      <main className="min-h-screen bg-primary-50/30">
        {/* Header */}
        <div className="bg-white border-b border-secondary-100">
          <div className="max-w-3xl mx-auto px-4 py-8 sm:py-12">
            {/* Breadcrumbs */}
            <nav className="text-sm text-secondary-500 mb-4" aria-label="Breadcrumb">
              <Link href="/" className="hover:text-primary-600">Home</Link>
              <span className="mx-2" aria-hidden>›</span>
              <Link href="/blog" className="hover:text-primary-600">Weekend Guides</Link>
              <span className="mx-2" aria-hidden>›</span>
              <span className="text-secondary-700 line-clamp-1">{post.title}</span>
            </nav>

            {/* Post type + area badges */}
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="inline-block bg-primary-100 text-primary-700 text-xs font-semibold px-2.5 py-1 rounded-full">
                {POST_TYPE_LABELS[post.post_type]}
              </span>
              {post.area !== 'nova' && (
                <span className="inline-block bg-secondary-50 text-secondary-600 text-xs font-medium px-2.5 py-1 rounded-full">
                  {AREA_LABELS[post.area]}
                </span>
              )}
              <span className="text-xs text-secondary-400">{dateRange}</span>
            </div>

            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-heading font-extrabold text-secondary-800 leading-tight">
              {post.title}
            </h1>

            {post.meta_description && (
              <p className="mt-3 text-base sm:text-lg text-secondary-600 leading-relaxed">
                {post.meta_description}
              </p>
            )}

            <p className="mt-4 text-sm text-secondary-400">
              {post.event_count} events · Updated{' '}
              {new Date(post.published_at).toLocaleDateString('en-US', {
                month: 'long', day: 'numeric', year: 'numeric',
              })}
            </p>
          </div>
        </div>

        {/* Blog content */}
        <div className="max-w-3xl mx-auto px-4 py-8 sm:py-12">
          {/* Markdown rendered as HTML */}
          <article
            className="prose prose-secondary max-w-none
              prose-headings:font-heading prose-headings:font-bold prose-headings:text-secondary-800
              prose-h2:text-xl prose-h2:mt-12 prose-h2:mb-5 prose-h2:border-b prose-h2:border-secondary-100 prose-h2:pb-2
              prose-h3:text-base prose-h3:text-secondary-700 prose-h3:mt-6 prose-h3:mb-2
              prose-p:text-secondary-700 prose-p:leading-relaxed prose-p:my-3
              prose-a:text-primary-600 prose-a:no-underline hover:prose-a:underline
              prose-strong:text-secondary-800 prose-strong:text-[1.0125rem]
              prose-ul:my-3 prose-li:my-1
              prose-hr:my-10"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(post.content) }}
          />

          {/* Event cards grid — visual anchor for the events mentioned in the post */}
          {post.events.length > 0 && (
            <section className="mt-14 pt-10 border-t border-secondary-100" aria-label="Events in this guide">
              <h2 className="text-xl font-heading font-bold text-secondary-800 mb-6">
                Events in This Guide
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {post.events.map(e => (
                  <EventCard key={e.id} event={eventPreviewToEvent(e)} />
                ))}
              </div>
            </section>
          )}

          {/* Footer CTAs */}
          <div className="mt-14 pt-8 border-t border-secondary-100 space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <Link
                href="/events"
                className="flex-1 text-center bg-primary-500 hover:bg-primary-600 text-white font-semibold px-5 py-3 rounded-lg transition-colors"
              >
                Browse all events →
              </Link>
              <Link
                href="/blog"
                className="flex-1 text-center bg-white hover:bg-secondary-50 text-secondary-700 border border-secondary-200 font-medium px-5 py-3 rounded-lg transition-colors"
              >
                More weekend guides
              </Link>
            </div>
            <p className="text-xs text-center text-secondary-400">
              New guides every Thursday evening at{' '}
              <Link href={`${SITE_URL}/blog`} className="text-primary-500 hover:underline">
                novakidlife.com/blog
              </Link>
            </p>
          </div>
        </div>
      </main>
    </>
  )
}


// ── Helpers ────────────────────────────────────────────────────────────────────

function formatDateRange(start: string, end: string): string {
  const s = new Date(start + 'T00:00:00')
  const e = new Date(end   + 'T00:00:00')
  const opts: Intl.DateTimeFormatOptions = { month: 'long', day: 'numeric' }
  if (s.getMonth() === e.getMonth()) {
    return `${s.toLocaleDateString('en-US', opts)}–${e.getDate()}, ${e.getFullYear()}`
  }
  return `${s.toLocaleDateString('en-US', opts)} – ${e.toLocaleDateString('en-US', { ...opts, year: 'numeric' })}`
}

/**
 * Block-based markdown → HTML converter.
 * Splits on blank lines first, then classifies each block.
 * This avoids the bug of wrapping block-level tags (h2, hr) in <p> tags.
 */
function renderMarkdown(md: string): string {
  const inline = (s: string) =>
    s
      // Arrow detail links → styled anchor
      .replace(
        /\[(→[^\]]*)\]\(([^)]+)\)/g,
        '<a href="$2" class="inline-block text-sm font-semibold text-primary-600 hover:text-primary-700 hover:underline">$1</a>',
      )
      // Bold
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      // Generic links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')

  const blocks = md.trim().split(/\n{2,}/)

  const rendered = blocks.map(block => {
    const lines = block.split('\n')
    const out: string[] = []
    const listBuf: string[] = []

    const flushList = () => {
      if (listBuf.length) {
        out.push(`<ul>${listBuf.join('')}</ul>`)
        listBuf.length = 0
      }
    }

    for (const raw of lines) {
      const line = raw.trimEnd()
      if (!line) continue

      if (/^### /.test(line)) { flushList(); out.push(`<h3>${inline(line.slice(4))}</h3>`); continue }
      if (/^## /.test(line))  { flushList(); out.push(`<h2>${inline(line.slice(3))}</h2>`); continue }
      if (/^# /.test(line))   { flushList(); out.push(`<h1>${inline(line.slice(2))}</h1>`); continue }
      if (line === '---')     { flushList(); out.push('<hr class="my-8 border-secondary-100" />'); continue }

      if (/^(📅|📍|💰)/.test(line)) {
        flushList()
        out.push(`<p class="text-sm text-secondary-500 my-0.5 leading-snug">${inline(line)}</p>`)
        continue
      }

      if (/^[-*] /.test(line)) { listBuf.push(`<li>${inline(line.slice(2))}</li>`); continue }

      flushList()
      out.push(`<p>${inline(line)}</p>`)
    }

    flushList()
    return out.join('\n')
  })

  return rendered.join('\n').replace(/<p>\s*<\/p>/g, '')
}

/**
 * Map EventPreview → Event shape expected by EventCard.
 * Only fills fields EventCard actually uses.
 */
function eventPreviewToEvent(e: BlogPostWithEvents['events'][number]): Event {
  return {
    id:               e.id,
    slug:             e.slug,
    title:            e.title,
    description:      '',
    start_at:         e.start_at,
    end_at:           null,
    location_name:    e.venue_name,
    location_address: e.location_text,
    lat:              null,
    lng:              null,
    event_type:       e.event_type as Event['event_type'],
    section:          'main',
    brand:            null,
    tags:             e.tags,
    age_min:          null,
    age_max:          null,
    is_free:          e.is_free,
    cost_description: e.cost_description,
    registration_url: null,
    image_url:        e.image_url_sm,
    image_url_md:     e.image_url_sm,
    image_url_sm:     e.image_url_sm,
    image_alt:        e.image_alt,
    image_blurhash:   e.image_blurhash,
    image_width:      e.image_width,
    image_height:     e.image_height,
    og_image_url:     null,
    social_image_url: null,
  } as Event
}
