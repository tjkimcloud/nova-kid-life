import type { Metadata } from 'next'
import Link from 'next/link'
import { NewsletterForm }       from '@/components/NewsletterForm'
import { HeroSearch }           from '@/components/HeroSearch'
import { WeekendEventsSection } from '@/components/WeekendEventsSection'
import { FreeEventsSection }    from '@/components/FreeEventsSection'
import { CityStripsSection }    from '@/components/CityStripsSection'

type BlogPost = {
  slug:              string
  title:             string
  post_type:         string
  meta_description?: string
  hero_image_url?:   string
  published_at:      string
  event_count?:      number
}

export const metadata: Metadata = {
  title: 'NovaKidLife — Family Events in Northern Virginia',
  description:
    'The most complete family events calendar for Northern Virginia. Free storytime, STEM workshops, outdoor adventures, birthday freebies, and Pokémon TCG events — updated weekly.',
  alternates: { canonical: 'https://novakidlife.com' },
  openGraph: {
    title:       'NovaKidLife — Family Events in Northern Virginia',
    description: 'The most complete family events calendar for Northern Virginia. Updated weekly from 100+ local sources.',
    type:        'website',
    url:         'https://novakidlife.com',
  },
}

// ── JSON-LD ──────────────────────────────────────────────────────────────────

const WEBSITE_SCHEMA = {
  '@context': 'https://schema.org',
  '@type':    'WebSite',
  name:        'NovaKidLife',
  url:         'https://novakidlife.com',
  description: 'Family events discovery platform for Northern Virginia',
  potentialAction: {
    '@type':       'SearchAction',
    target: {
      '@type':     'EntryPoint',
      urlTemplate: 'https://novakidlife.com/events?q={search_term_string}',
    },
    'query-input': 'required name=search_term_string',
  },
}

const LOCAL_BUSINESS_SCHEMA = {
  '@context': 'https://schema.org',
  '@type':    'LocalBusiness',
  name:        'NovaKidLife',
  url:         'https://novakidlife.com',
  description: 'The most complete family events guide for Northern Virginia — Fairfax, Loudoun, Arlington, and Prince William counties.',
  areaServed: [
    { '@type': 'County', name: 'Fairfax County',        containedInPlace: { '@type': 'State', name: 'Virginia' } },
    { '@type': 'County', name: 'Loudoun County',        containedInPlace: { '@type': 'State', name: 'Virginia' } },
    { '@type': 'County', name: 'Arlington County',      containedInPlace: { '@type': 'State', name: 'Virginia' } },
    { '@type': 'County', name: 'Prince William County', containedInPlace: { '@type': 'State', name: 'Virginia' } },
  ],
  knowsAbout: ['Family Events', 'Kids Activities', 'Northern Virginia', 'Pokémon TCG Events'],
}

// ── Static data ───────────────────────────────────────────────────────────────

const INTEREST_LINKS = [
  { label: 'Free Events',    href: '/events?free=true'                  },
  { label: 'This Weekend',   href: '/events?date=weekend'               },
  { label: 'Storytime',      href: '/events?category=storytime'         },
  { label: 'STEM & Science', href: '/events?category=stem'              },
  { label: 'Outdoors',       href: '/events?category=outdoor'           },
  { label: 'Birthday Deals', href: '/events?category=birthday_freebie'  },
  { label: 'Pokémon TCG',    href: '/pokemon'                           },
]

const POST_TYPE_LABELS: Record<string, string> = {
  weekend:    'Weekend Guide',
  week_ahead: 'Weekly Guide',
  free:       'Free Events',
  location:   'Local Guide',
  seasonal:   'Seasonal Guide',
  indoor:     'Indoor Guide',
}

async function fetchBlogPosts(): Promise<BlogPost[]> {
  try {
    const base = process.env.NEXT_PUBLIC_API_URL || 'https://api.novakidlife.com'
    const res = await fetch(`${base}/blog?limit=4`, {
      signal: AbortSignal.timeout(8000),
      next:   { revalidate: 3600 },
    })
    if (!res.ok) return []
    const data = await res.json()
    return data.items || []
  } catch {
    return []
  }
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default async function HomePage() {
  const livePosts = await fetchBlogPosts()
  const [featuredPost, ...morePosts] = livePosts

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(WEBSITE_SCHEMA) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(LOCAL_BUSINESS_SCHEMA) }}
      />

      <main>

        {/* ── Hero — photo background with warm overlay ── */}
        <section className="relative overflow-hidden min-h-[520px] sm:min-h-[580px] flex flex-col justify-end">
          {/* Photo background */}
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat bg-primary-700"
            style={{ backgroundImage: "url('/images/hero-family.jpg')" }}
            aria-hidden="true"
          />
          {/* Warm overlay — left-heavy for text legibility */}
          <div
            className="absolute inset-0 bg-gradient-to-r from-primary-950/90 via-primary-900/70 to-primary-700/30"
            aria-hidden="true"
          />
          {/* Bottom fade into search section */}
          <div
            className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-amber-50 to-transparent"
            aria-hidden="true"
          />

          <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20">
            <p className="text-primary-200 text-xs sm:text-sm font-bold uppercase tracking-widest mb-3">
              Family Events · Northern Virginia
            </p>
            <h1 className="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-white leading-tight text-balance max-w-2xl mb-5">
              Your family&apos;s next adventure{' '}
              <span className="text-amber-300">starts here</span>
            </h1>
            <p className="text-white/75 text-base sm:text-lg max-w-xl mb-8 leading-relaxed">
              Storytime, STEM, outdoor adventures, birthday freebies, and Pokémon TCG —
              curated every week from 100+ NoVa sources.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/events"
                className="inline-flex items-center gap-2 bg-white text-primary-700 font-bold px-6 py-3 rounded-full text-sm hover:bg-primary-50 transition-colors shadow-md"
              >
                Browse all events
              </Link>
              <Link
                href="/events?free=true"
                className="inline-flex items-center border-2 border-white/50 text-white font-semibold px-6 py-3 rounded-full text-sm hover:border-white transition-colors"
              >
                Free this weekend
              </Link>
            </div>
          </div>
        </section>

        {/* ── Search ── */}
        <section className="bg-amber-50 pt-2 pb-10">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <HeroSearch />
          </div>
        </section>

        {/* ── Featured editorial post ── */}
        {featuredPost && (
          <section className="py-12 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <p className="text-xs font-bold uppercase tracking-widest text-primary-500 mb-5">
                Latest Family Guide
              </p>
              <Link
                href={`/blog/${featuredPost.slug}`}
                className="group block rounded-3xl overflow-hidden border border-primary-100 hover:shadow-xl transition-all duration-300 bg-primary-50"
              >
                <div className="grid md:grid-cols-5 items-stretch min-h-[260px]">
                  {/* Image — 3 of 5 columns on desktop */}
                  <div className="md:col-span-3 relative overflow-hidden bg-primary-200 min-h-[220px] md:min-h-0">
                    {featuredPost.hero_image_url ? (
                      <img
                        src={featuredPost.hero_image_url}
                        alt={featuredPost.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        loading="eager"
                      />
                    ) : (
                      <div className="absolute inset-0 bg-gradient-to-br from-primary-400 to-primary-700 flex items-end p-8">
                        <span className="font-heading font-extrabold text-[140px] leading-none text-white/10 select-none">
                          {(POST_TYPE_LABELS[featuredPost.post_type] ?? 'G')[0]}
                        </span>
                      </div>
                    )}
                  </div>
                  {/* Content — 2 of 5 columns */}
                  <div className="md:col-span-2 p-8 md:p-10 flex flex-col justify-center">
                    <span className="text-xs font-bold uppercase tracking-widest text-primary-500 mb-3">
                      {POST_TYPE_LABELS[featuredPost.post_type] ?? 'Guide'}
                    </span>
                    <h2 className="font-heading font-extrabold text-xl sm:text-2xl text-secondary-900 group-hover:text-primary-700 transition-colors leading-snug mb-4">
                      {featuredPost.title}
                    </h2>
                    {featuredPost.meta_description && (
                      <p className="text-secondary-500 text-sm leading-relaxed mb-5 line-clamp-3">
                        {featuredPost.meta_description}
                      </p>
                    )}
                    {featuredPost.event_count != null && featuredPost.event_count > 0 && (
                      <p className="text-xs text-secondary-400 mb-4">
                        {featuredPost.event_count} events included
                      </p>
                    )}
                    <span className="text-primary-600 font-semibold text-sm group-hover:text-primary-700 transition-colors">
                      Read the guide →
                    </span>
                  </div>
                </div>
              </Link>
            </div>
          </section>
        )}

        {/* ── Weekend events ── */}
        <WeekendEventsSection />

        {/* ── Browse by interest ── */}
        <section className="py-10 bg-white border-t border-secondary-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <p className="text-xs font-bold uppercase tracking-widest text-secondary-400 mb-4">
              Browse by interest
            </p>
            <div className="flex flex-wrap gap-2">
              {INTEREST_LINKS.map(({ label, href }) => (
                <Link
                  key={label}
                  href={href}
                  className="px-4 py-2 rounded-full border border-secondary-200 bg-white text-sm font-semibold text-secondary-700 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700 transition-colors"
                >
                  {label}
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── Free events spotlight ── */}
        <FreeEventsSection />

        {/* ── More guides ── */}
        {morePosts.length > 0 && (
          <section className="py-14 bg-secondary-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-heading font-bold text-xl text-secondary-900">
                  More Family Guides
                </h2>
                <Link
                  href="/blog"
                  className="text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors whitespace-nowrap"
                >
                  All guides →
                </Link>
              </div>
              <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {morePosts.map(post => (
                  <li key={post.slug}>
                    <Link
                      href={`/blog/${post.slug}`}
                      className="group flex flex-col h-full rounded-2xl overflow-hidden border border-secondary-100 bg-white hover:shadow-md transition-shadow"
                    >
                      <div className="relative overflow-hidden bg-secondary-100 h-44">
                        {post.hero_image_url ? (
                          <img
                            src={post.hero_image_url}
                            alt={post.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                            loading="lazy"
                          />
                        ) : (
                          <div className="absolute inset-0 bg-gradient-to-br from-secondary-300 to-secondary-500 flex items-center justify-center">
                            <span className="font-heading font-extrabold text-7xl text-white/20 select-none">
                              {(POST_TYPE_LABELS[post.post_type] ?? 'G')[0]}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="p-5 flex flex-col flex-1">
                        <span className="text-[10px] font-bold uppercase tracking-widest text-secondary-400 mb-2">
                          {POST_TYPE_LABELS[post.post_type] ?? 'Guide'}
                        </span>
                        <h3 className="font-heading font-bold text-sm text-secondary-900 group-hover:text-primary-700 transition-colors leading-snug flex-1">
                          {post.title}
                        </h3>
                        <span className="mt-4 text-xs font-semibold text-primary-600">
                          Read guide →
                        </span>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}

        {/* ── Events by city ── */}
        <CityStripsSection />

        {/* ── Coverage area ── */}
        <section className="py-12 bg-secondary-50">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-heading font-bold text-xl text-secondary-900 mb-3">
              Covering All of Northern Virginia
            </h2>
            <p className="text-secondary-500 mb-6 text-sm max-w-xl mx-auto">
              From Leesburg to Woodbridge, Reston to Manassas — across Fairfax, Loudoun, Arlington, and Prince William counties.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                'Fairfax', 'Reston', 'Herndon', 'Chantilly', 'McLean',
                'Leesburg', 'Ashburn', 'Sterling', 'Manassas', 'Woodbridge',
                'Arlington', 'Alexandria', 'Vienna', 'Springfield', 'Centreville',
              ].map((city) => (
                <Link
                  key={city}
                  href={`/events?q=${city}`}
                  className="px-3 py-1.5 rounded-full text-xs font-medium bg-white border border-secondary-200 text-secondary-600 hover:border-primary-300 hover:text-primary-700 transition-colors"
                >
                  {city}, VA
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── Newsletter CTA ── */}
        <section className="py-16 bg-secondary-800">
          <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-heading font-bold text-2xl text-white mb-3">
              Never Miss a NoVa Family Event
            </h2>
            <p className="text-secondary-300 mb-6 text-sm">
              Weekly roundup of the best events, deals, and freebies for Northern Virginia families. Free. No spam.
            </p>
            <NewsletterForm />
          </div>
        </section>

      </main>
    </>
  )
}
