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
    target: { '@type': 'EntryPoint', urlTemplate: 'https://novakidlife.com/events?q={search_term_string}' },
    'query-input': 'required name=search_term_string',
  },
}

const LOCAL_BUSINESS_SCHEMA = {
  '@context': 'https://schema.org',
  '@type':    'LocalBusiness',
  name:        'NovaKidLife',
  url:         'https://novakidlife.com',
  description: 'The most complete family events guide for Northern Virginia.',
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
  { label: 'Free Events',    href: '/events?free=true'                 },
  { label: 'This Weekend',   href: '/events?date=weekend'              },
  { label: 'Storytime',      href: '/events?category=storytime'        },
  { label: 'STEM & Science', href: '/events?category=stem'             },
  { label: 'Outdoors',       href: '/events?category=outdoor'          },
  { label: 'Birthday Deals', href: '/events?category=birthday_freebie' },
  { label: 'Pokémon TCG',    href: '/pokemon'                          },
]

const STATS = [
  { value: '100+',   label: 'Local sources'  },
  { value: 'Weekly', label: 'Updated'        },
  { value: '4',      label: 'NoVa counties'  },
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
    const res  = await fetch(`${base}/blog?limit=4`, {
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
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(WEBSITE_SCHEMA) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(LOCAL_BUSINESS_SCHEMA) }} />

      <main style={{ background: 'var(--bg)' }}>

        {/* ── Hero ─────────────────────────────────────────────────────── */}
        <section
          className="relative overflow-hidden min-h-[500px] sm:min-h-[560px] flex flex-col justify-end"
          style={{ background: 'var(--bg)' }}
        >
          {/* Photo background */}
          <div
            className="absolute inset-0 bg-cover bg-center bg-no-repeat"
            style={{ backgroundImage: "url('/images/hero-family-meadow-v2.jpg')", backgroundColor: '#3a5a3a', backgroundPosition: 'center 30%' }}
            aria-hidden="true"
          />
          {/* Warm overlay — left-to-right so text stays readable, right side lets photo breathe */}
          <div
            className="absolute inset-0"
            style={{ background: 'linear-gradient(105deg, rgba(30,20,10,0.82) 0%, rgba(50,30,10,0.65) 45%, rgba(100,50,15,0.25) 100%)' }}
            aria-hidden="true"
          />
          {/* Bottom fade into page */}
          <div
            className="absolute bottom-0 left-0 right-0 h-16"
            style={{ background: 'linear-gradient(to top, var(--bg), transparent)' }}
            aria-hidden="true"
          />

          <div className="relative max-w-content mx-auto w-full px-5 lg:px-8 pt-20 pb-16 sm:pb-20">

            {/* Eyebrow */}
            <div
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[11px] font-body font-bold uppercase tracking-widest mb-5"
              style={{ background: 'rgba(255,240,230,0.15)', color: '#FFD4B8', border: '1px solid rgba(255,200,160,0.25)' }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full shrink-0"
                style={{ background: '#FF8C55', animation: 'pulse 2s ease-in-out infinite' }}
                aria-hidden="true"
              />
              Northern Virginia&apos;s #1 family guide
            </div>

            {/* H1 */}
            <h1
              className="font-heading font-extrabold text-white text-balance max-w-xl mb-5"
              style={{ fontSize: 'clamp(32px, 7vw, 52px)', lineHeight: 1.1, letterSpacing: '-1px' }}
            >
              Find something{' '}
              <span className="relative inline-block" style={{ color: '#FF8C55' }}>
                fun
                <span
                  className="absolute left-0 right-0 bottom-1 rounded-full"
                  style={{ height: '5px', background: '#FF8C55', opacity: 0.35 }}
                  aria-hidden="true"
                />
              </span>
              {' '}to do this weekend.
            </h1>

            {/* Subtitle */}
            <p
              className="font-body text-base sm:text-lg max-w-md mb-8 leading-relaxed"
              style={{ color: 'rgba(255,248,242,0.75)' }}
            >
              Storytime, STEM, outdoor adventures, birthday freebies, and Pokémon TCG —
              curated every week from 100+ NoVa sources.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap gap-3">
              <Link
                href="/events"
                className="inline-flex items-center gap-2 font-body font-semibold text-sm text-white px-6 py-3 rounded-full transition-all hover:-translate-y-0.5"
                style={{ background: 'var(--orange)', boxShadow: 'var(--shadow-orange)' }}
              >
                Browse all events
              </Link>
              <Link
                href="/events?free=true"
                className="inline-flex items-center font-body font-semibold text-sm px-6 py-3 rounded-full transition-colors"
                style={{ background: 'rgba(255,255,255,0.12)', color: '#fff', border: '1.5px solid rgba(255,255,255,0.35)' }}
              >
                Free this weekend
              </Link>
            </div>

            {/* Stats */}
            <div
              className="flex flex-wrap gap-6 mt-8 pt-6"
              style={{ borderTop: '1px solid rgba(255,255,255,0.15)' }}
            >
              {STATS.map(({ value, label }) => (
                <div key={label}>
                  <p className="font-heading font-extrabold text-xl text-white leading-none">{value}</p>
                  <p className="font-body text-[11px] mt-0.5" style={{ color: 'rgba(255,248,242,0.6)' }}>{label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Search ───────────────────────────────────────────────────── */}
        <section className="pt-2 pb-10" style={{ background: 'var(--bg)' }}>
          <div className="max-w-content mx-auto px-5 lg:px-8">
            <HeroSearch />
          </div>
        </section>

        {/* ── Featured editorial post ──────────────────────────────────── */}
        {featuredPost && (
          <section className="py-10" style={{ background: 'var(--bg)' }}>
            <div className="max-w-content mx-auto px-5 lg:px-8">
              <p
                className="font-body text-[10px] font-bold uppercase tracking-widest mb-4"
                style={{ color: 'var(--orange)' }}
              >
                Latest Family Guide
              </p>
              <Link
                href={`/blog/${featuredPost.slug}`}
                className="group block overflow-hidden border border-secondary-200 transition-all duration-300 hover:-translate-y-0.5"
                style={{ borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)', background: 'var(--white)' }}
              >
                <div className="grid md:grid-cols-5 items-stretch min-h-[240px]">
                  {/* Image — 3 of 5 cols */}
                  <div className="md:col-span-3 relative overflow-hidden min-h-[200px] md:min-h-0 bg-secondary-100">
                    {featuredPost.hero_image_url ? (
                      <img
                        src={featuredPost.hero_image_url}
                        alt={featuredPost.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        loading="eager"
                      />
                    ) : (
                      <div
                        className="absolute inset-0 flex items-end p-8"
                        style={{ background: 'linear-gradient(135deg, var(--orange-pale), #ffdac0)' }}
                      >
                        <span
                          className="font-heading font-extrabold leading-none select-none"
                          style={{ fontSize: '120px', color: 'rgba(232,93,26,0.12)' }}
                        >
                          {(POST_TYPE_LABELS[featuredPost.post_type] ?? 'G')[0]}
                        </span>
                      </div>
                    )}
                  </div>
                  {/* Content — 2 of 5 cols */}
                  <div className="md:col-span-2 p-7 md:p-9 flex flex-col justify-center">
                    <span
                      className="font-body text-[10px] font-bold uppercase tracking-widest mb-3"
                      style={{ color: 'var(--orange)' }}
                    >
                      {POST_TYPE_LABELS[featuredPost.post_type] ?? 'Guide'}
                    </span>
                    <h2
                      className="font-heading font-extrabold text-xl sm:text-2xl leading-snug mb-3 transition-colors group-hover:text-primary-500"
                      style={{ color: 'var(--text)', letterSpacing: '-0.3px' }}
                    >
                      {featuredPost.title}
                    </h2>
                    {featuredPost.meta_description && (
                      <p
                        className="font-body text-sm leading-relaxed mb-4 line-clamp-3"
                        style={{ color: 'var(--text2)' }}
                      >
                        {featuredPost.meta_description}
                      </p>
                    )}
                    {featuredPost.event_count != null && featuredPost.event_count > 0 && (
                      <p className="font-body text-[11px] mb-4" style={{ color: 'var(--text3)' }}>
                        {featuredPost.event_count} events included
                      </p>
                    )}
                    <span
                      className="font-body text-sm font-semibold transition-colors group-hover:text-primary-600"
                      style={{ color: 'var(--orange)' }}
                    >
                      Read the guide →
                    </span>
                  </div>
                </div>
              </Link>
            </div>
          </section>
        )}

        {/* ── Weekend events ────────────────────────────────────────────── */}
        <WeekendEventsSection />

        {/* ── Browse by interest ───────────────────────────────────────── */}
        <section className="py-8 border-t border-secondary-200" style={{ background: 'var(--bg)' }}>
          <div className="max-w-content mx-auto px-5 lg:px-8">
            <p
              className="font-body text-[10px] font-bold uppercase tracking-widest mb-4"
              style={{ color: 'var(--text3)' }}
            >
              Browse by interest
            </p>
            <div className="flex flex-wrap gap-2">
              {INTEREST_LINKS.map(({ label, href }) => (
                <Link
                  key={label}
                  href={href}
                  className="font-body font-semibold text-sm px-4 py-2 rounded-full border border-secondary-200 transition-colors hover:border-primary-400 hover:text-primary-500 hover:bg-primary-50"
                  style={{ color: 'var(--text2)', background: 'var(--white)' }}
                >
                  {label}
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── Free events ───────────────────────────────────────────────── */}
        <FreeEventsSection />

        {/* ── More guides ──────────────────────────────────────────────── */}
        {morePosts.length > 0 && (
          <section className="py-12 border-t border-secondary-200" style={{ background: 'var(--bg2)' }}>
            <div className="max-w-content mx-auto px-5 lg:px-8">
              <div className="flex items-center justify-between mb-6">
                <h2
                  className="font-heading font-extrabold text-[19px]"
                  style={{ color: 'var(--text)', letterSpacing: '-0.3px' }}
                >
                  More Family Guides
                </h2>
                <Link
                  href="/blog"
                  className="font-body text-sm font-semibold transition-colors hover:text-primary-600"
                  style={{ color: 'var(--orange)' }}
                >
                  All guides →
                </Link>
              </div>
              <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {morePosts.map(post => (
                  <li key={post.slug}>
                    <Link
                      href={`/blog/${post.slug}`}
                      className="group flex flex-col h-full overflow-hidden border border-secondary-200 transition-all duration-200 hover:-translate-y-0.5"
                      style={{ borderRadius: 'var(--radius-lg)', background: 'var(--white)', boxShadow: 'var(--shadow-sm)' }}
                    >
                      <div className="relative overflow-hidden h-40 bg-secondary-100">
                        {post.hero_image_url ? (
                          <img
                            src={post.hero_image_url}
                            alt={post.title}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                            loading="lazy"
                          />
                        ) : (
                          <div
                            className="absolute inset-0 flex items-center justify-center"
                            style={{ background: 'linear-gradient(135deg, var(--bg2), var(--bg3))' }}
                          >
                            <span
                              className="font-heading font-extrabold select-none"
                              style={{ fontSize: '72px', color: 'rgba(164,149,136,0.35)' }}
                            >
                              {(POST_TYPE_LABELS[post.post_type] ?? 'G')[0]}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="p-5 flex flex-col flex-1">
                        <span
                          className="font-body text-[10px] font-bold uppercase tracking-widest mb-2"
                          style={{ color: 'var(--text3)' }}
                        >
                          {POST_TYPE_LABELS[post.post_type] ?? 'Guide'}
                        </span>
                        <h3
                          className="font-heading font-bold text-[15px] leading-snug flex-1 transition-colors group-hover:text-primary-500"
                          style={{ color: 'var(--text)', letterSpacing: '-0.1px' }}
                        >
                          {post.title}
                        </h3>
                        <span
                          className="mt-4 font-body text-xs font-semibold"
                          style={{ color: 'var(--orange)' }}
                        >
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

        {/* ── Events by city ───────────────────────────────────────────── */}
        <CityStripsSection />

        {/* ── Coverage area ────────────────────────────────────────────── */}
        <section className="py-10 border-t border-secondary-200" style={{ background: 'var(--bg)' }}>
          <div className="max-w-content mx-auto px-5 lg:px-8 text-center">
            <h2
              className="font-heading font-extrabold text-[19px] mb-2"
              style={{ color: 'var(--text)', letterSpacing: '-0.3px' }}
            >
              Covering All of Northern Virginia
            </h2>
            <p className="font-body text-sm mb-6 max-w-md mx-auto" style={{ color: 'var(--text2)' }}>
              From Leesburg to Woodbridge, Reston to Manassas — Fairfax, Loudoun, Arlington, and Prince William counties.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {[
                'Fairfax','Reston','Herndon','Chantilly','McLean',
                'Leesburg','Ashburn','Sterling','Manassas','Woodbridge',
                'Arlington','Alexandria','Vienna','Springfield','Centreville',
              ].map((city) => (
                <Link
                  key={city}
                  href={`/events?q=${city}`}
                  className="font-body text-xs font-medium px-3 py-1.5 rounded-full border border-secondary-200 transition-colors hover:border-primary-400 hover:text-primary-500"
                  style={{ color: 'var(--text2)', background: 'var(--white)' }}
                >
                  {city}, VA
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* ── Newsletter ───────────────────────────────────────────────── */}
        <section
          className="py-14"
          style={{ background: 'var(--orange-pale)', borderTop: '1px solid var(--border)' }}
        >
          <div className="max-w-content mx-auto px-5 lg:px-8 text-center">
            <h2
              className="font-heading font-extrabold text-2xl sm:text-3xl mb-2"
              style={{ color: 'var(--text)', letterSpacing: '-0.5px' }}
            >
              Never Miss a NoVa Family Event
            </h2>
            <p className="font-body text-sm mb-7 max-w-sm mx-auto" style={{ color: 'var(--text2)' }}>
              Weekly roundup of the best events, deals, and freebies. Free. No spam.
            </p>
            <NewsletterForm />
          </div>
        </section>

      </main>
    </>
  )
}
