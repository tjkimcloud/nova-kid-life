import type { Metadata } from 'next'
import Link from 'next/link'
import { getBlogPosts } from '@/lib/api'
import { POST_TYPE_LABELS, AREA_LABELS } from '@/types/blog'
import type { BlogPost } from '@/types/blog'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://novakidlife.com'

export const metadata: Metadata = {
  title: 'Things To Do With Kids in Northern Virginia — Weekend Roundups',
  description:
    'Weekly guides to family events in Northern Virginia. Things to do this weekend in Fairfax, Loudoun, Arlington, and Alexandria — updated every Thursday.',
  openGraph: {
    title:       'Things To Do With Kids in Northern Virginia | NovaKidLife',
    description: 'Weekly weekend roundups for NoVa parents. Free events, indoor activities, and the best things to do with kids this weekend.',
    type:        'website',
    url:         `${SITE_URL}/blog`,
  },
  alternates: {
    canonical: `${SITE_URL}/blog`,
  },
}

const BLOG_LIST_SCHEMA = {
  '@context': 'https://schema.org',
  '@type':    'Blog',
  name:       'NovaKidLife — Things To Do With Kids in Northern Virginia',
  description:'Weekly family event roundups for Northern Virginia parents.',
  url:        `${SITE_URL}/blog`,
  publisher: {
    '@type': 'Organization',
    name:    'NovaKidLife',
    url:     SITE_URL,
  },
}

export default async function BlogPage() {
  let posts: BlogPost[] = []

  try {
    const data = await getBlogPosts({ limit: 24 })
    posts = data.items
  } catch {
    // API unavailable at build time — render empty state gracefully
  }

  // Pin the main weekend roundup to the top
  const pinned  = posts.find(p => p.post_type === 'weekend_roundup' && p.area === 'nova')
  const rest    = posts.filter(p => p !== pinned)

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(BLOG_LIST_SCHEMA) }}
      />

      <main className="min-h-screen bg-primary-50/30">
        {/* Header */}
        <div className="bg-white border-b border-secondary-100">
          <div className="max-w-5xl mx-auto px-4 py-10 sm:py-14">
            <nav className="text-sm text-secondary-500 mb-3" aria-label="Breadcrumb">
              <Link href="/" className="hover:text-primary-600">Home</Link>
              <span className="mx-2" aria-hidden>›</span>
              <span className="text-secondary-700">Weekend Guides</span>
            </nav>
            <h1 className="text-3xl sm:text-4xl font-heading font-extrabold text-secondary-800 leading-tight">
              Things To Do With Kids in Northern Virginia
            </h1>
            <p className="mt-3 text-lg text-secondary-600 max-w-2xl">
              Updated every Thursday — every free event, farm day, storytime, and outdoor
              adventure worth loading the kids into the car for this weekend.
            </p>
          </div>
        </div>

        <div className="max-w-5xl mx-auto px-4 py-8 sm:py-12">
          {posts.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="space-y-12">
              {/* Pinned: main weekend roundup */}
              {pinned && (
                <section aria-label="This weekend's roundup">
                  <h2 className="text-xs font-semibold uppercase tracking-widest text-primary-600 mb-4">
                    This Weekend
                  </h2>
                  <PinnedCard post={pinned} />
                </section>
              )}

              {/* Rest of posts */}
              {rest.length > 0 && (
                <section aria-label="More guides">
                  <h2 className="text-xs font-semibold uppercase tracking-widest text-secondary-400 mb-4">
                    More Guides
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {rest.map(post => (
                      <PostCard key={post.id} post={post} />
                    ))}
                  </div>
                </section>
              )}
            </div>
          )}

          {/* CTA to events */}
          <div className="mt-14 py-8 border-t border-secondary-100 text-center">
            <p className="text-secondary-600 mb-3">Looking for a specific event?</p>
            <Link
              href="/events"
              className="inline-block bg-primary-500 hover:bg-primary-600 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              Browse all Northern Virginia events →
            </Link>
          </div>
        </div>
      </main>
    </>
  )
}


// ── Sub-components ─────────────────────────────────────────────────────────────

function PinnedCard({ post }: { post: BlogPost }) {
  const dateRange = formatDateRange(post.date_range_start, post.date_range_end)
  return (
    <Link
      href={`/blog/${post.slug}`}
      className="group block bg-white rounded-2xl border border-secondary-100 hover:border-primary-300 shadow-sm hover:shadow-md transition-all overflow-hidden"
    >
      <div className="p-6 sm:p-8">
        <div className="flex items-center gap-2 mb-3">
          <span className="inline-block bg-primary-100 text-primary-700 text-xs font-semibold px-2.5 py-1 rounded-full">
            {POST_TYPE_LABELS[post.post_type]}
          </span>
          <span className="text-xs text-secondary-400">{dateRange}</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-heading font-bold text-secondary-800 group-hover:text-primary-700 transition-colors leading-snug">
          {post.title}
        </h2>
        {post.meta_description && (
          <p className="mt-2 text-secondary-600 text-base leading-relaxed line-clamp-2">
            {post.meta_description}
          </p>
        )}
        <div className="mt-4 flex items-center gap-4 text-sm text-secondary-400">
          <span>{post.event_count} events</span>
          <span>·</span>
          <span className="text-primary-600 font-medium group-hover:underline">
            Read the guide →
          </span>
        </div>
      </div>
    </Link>
  )
}

function PostCard({ post }: { post: BlogPost }) {
  const dateRange = formatDateRange(post.date_range_start, post.date_range_end)
  return (
    <Link
      href={`/blog/${post.slug}`}
      className="group block bg-white rounded-xl border border-secondary-100 hover:border-primary-300 shadow-sm hover:shadow-md transition-all p-5"
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="inline-block bg-secondary-50 text-secondary-500 text-xs font-medium px-2 py-0.5 rounded-full">
          {POST_TYPE_LABELS[post.post_type]}
        </span>
        {post.area !== 'nova' && (
          <span className="text-xs text-secondary-400">{AREA_LABELS[post.area]}</span>
        )}
      </div>
      <h3 className="font-heading font-bold text-secondary-800 group-hover:text-primary-700 transition-colors leading-snug line-clamp-2">
        {post.title}
      </h3>
      <div className="mt-3 flex items-center justify-between text-sm text-secondary-400">
        <span>{dateRange}</span>
        <span>{post.event_count} events</span>
      </div>
    </Link>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-20">
      <p className="text-secondary-500 text-lg mb-2">Weekend guides are generated every Thursday.</p>
      <p className="text-secondary-400 text-sm mb-6">Check back Thursday evening for this weekend's roundup.</p>
      <Link
        href="/events"
        className="inline-block text-primary-600 hover:text-primary-700 font-medium underline underline-offset-2"
      >
        Browse all events in the meantime →
      </Link>
    </div>
  )
}


// ── Helpers ────────────────────────────────────────────────────────────────────

function formatDateRange(start: string, end: string): string {
  const s = new Date(start + 'T00:00:00')
  const e = new Date(end   + 'T00:00:00')
  const opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' }
  if (s.getMonth() === e.getMonth()) {
    return `${s.toLocaleDateString('en-US', opts)}–${e.getDate()}`
  }
  return `${s.toLocaleDateString('en-US', opts)} – ${e.toLocaleDateString('en-US', opts)}`
}
