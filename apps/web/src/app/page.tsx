import type { Metadata } from 'next'
import Link from 'next/link'
import { NewsletterForm }      from '@/components/NewsletterForm'
import { HeroSearch }          from '@/components/HeroSearch'
import { WeekendEventsSection } from '@/components/WeekendEventsSection'
import { FreeEventsSection }   from '@/components/FreeEventsSection'
import { CityStripsSection }   from '@/components/CityStripsSection'

type BlogPost = {
  slug:       string
  title:      string
  post_type:  string
  created_at: string
  excerpt?:   string
}

export const metadata: Metadata = {
  title: 'NovaKidLife — Family Events in Northern Virginia',
  description:
    'The most complete family events calendar for Northern Virginia. Free storytime, STEM workshops, outdoor adventures, birthday freebies, and Pokémon TCG events — updated daily.',
  alternates: { canonical: 'https://novakidlife.com' },
  openGraph: {
    title:       'NovaKidLife — Family Events in Northern Virginia',
    description: 'The most complete family events calendar for Northern Virginia. Updated daily from 59+ local sources.',
    type:        'website',
    url:         'https://novakidlife.com',
  },
}

// ── JSON-LD ─────────────────────────────────────────────────────────────────

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

// ── Static data ──────────────────────────────────────────────────────────────

const AGE_GROUPS = [
  { emoji: '🍼', label: 'Toddlers',   sub: 'Ages 0–3',  href: '/events?age_min=0&age_max=3'  },
  { emoji: '🎨', label: 'Little Kids', sub: 'Ages 4–7',  href: '/events?age_min=4&age_max=7'  },
  { emoji: '🔬', label: 'Big Kids',   sub: 'Ages 8–12', href: '/events?age_min=8&age_max=12' },
  { emoji: '🎮', label: 'Teens',      sub: 'Ages 13+',  href: '/events?age_min=13'            },
]

const CATEGORIES = [
  { emoji: '📚', label: 'Storytime',   desc: 'Library storytimes for toddlers & kids',     href: '/events?category=storytime'       },
  { emoji: '🔬', label: 'STEM',        desc: 'Science, tech & engineering workshops',       href: '/events?category=stem'            },
  { emoji: '🌳', label: 'Outdoors',    desc: 'Hikes, farms, nature programs & more',       href: '/events?category=outdoor'         },
  { emoji: '🎁', label: 'Free Events', desc: 'Zero cost — just show up',                   href: '/events?free=true'                },
  { emoji: '🎂', label: 'Freebies',    desc: 'Birthday freebies & restaurant deals',       href: '/events?category=birthday_freebie'},
  { emoji: '🃏', label: 'Pokémon TCG', desc: 'Leagues, prereleases & tournaments in NoVa', href: '/pokemon'                         },
]

const BLOG_POSTS = [
  {
    category: 'Rainy Day',
    title:    'Rainy Day Activities for Kids in Northern Virginia',
    desc:     '25 indoor spots — from trampoline parks to escape rooms — that keep kids busy when the weather turns.',
    href:     '/events',
    emoji:    '🌧️',
    featured: true,
  },
  {
    category: 'Guide',
    title:    'Best Free Things To Do With Kids in Fairfax County',
    desc:     'Libraries, parks, museums, and community events that cost nothing.',
    href:     '/events?q=Fairfax&free=true',
    emoji:    '🏛️',
  },
  {
    category: 'Pokémon',
    title:    'NoVa Pokémon TCG Event Guide for 2025',
    desc:     'Every league, prerelease, and regional championship happening in Northern Virginia.',
    href:     '/pokemon',
    emoji:    '🃏',
  },
]

const STATS = [
  { value: '59+',  label: 'Local sources' },
  { value: '4',    label: 'NoVa counties' },
  { value: 'Free', label: 'Always free'   },
  { value: 'Daily', label: 'Updated'      },
]

async function fetchBlogPosts(): Promise<BlogPost[]> {
  try {
    const base = process.env.NEXT_PUBLIC_API_URL || 'https://api.novakidlife.com'
    const res = await fetch(`${base}/blog?limit=3`, {
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

// ── Page ─────────────────────────────────────────────────────────────────────

export default async function HomePage() {
  const livePosts = await fetchBlogPosts()
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

        {/* ── Hero ── */}
        <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-500 to-primary-700 pb-12 pt-16">
          {/* Decorative background orbs */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
            <div className="absolute -top-20 -right-20 w-96 h-96 rounded-full bg-white/5 blur-3xl" />
            <div className="absolute bottom-0 -left-10 w-64 h-64 rounded-full bg-primary-400/30 blur-2xl" />
          </div>

          <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-10">
              <h1 className="font-heading font-extrabold text-4xl sm:text-5xl text-white leading-tight text-balance">
                Find Family Events in{' '}
                <span className="text-amber-300">Northern Virginia</span>
              </h1>
              <p className="mt-4 text-lg text-white/80 max-w-2xl mx-auto leading-relaxed text-balance">
                Free storytime, STEM workshops, outdoor adventures, birthday freebies,
                and Pokémon TCG — updated daily from 59+ local sources.
              </p>
            </div>

            <HeroSearch />
          </div>
        </section>

        {/* ── Stats bar ── */}
        <section className="bg-secondary-900 py-6" aria-label="Site statistics">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <dl className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
              {STATS.map(({ value, label }) => (
                <div key={label}>
                  <dt className="font-heading font-extrabold text-2xl text-primary-400">{value}</dt>
                  <dd className="mt-0.5 text-xs text-secondary-400">{label}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* ── Browse by category ── */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="font-heading font-bold text-2xl text-secondary-900 mb-8 text-center">
              What Are You Looking For?
            </h2>
            <ul className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              {CATEGORIES.map(({ emoji, label, desc, href }) => (
                <li key={label}>
                  <Link
                    href={href}
                    className="flex flex-col items-center gap-2 p-5 rounded-2xl border border-secondary-100 bg-white hover:border-primary-200 hover:bg-primary-50 transition-colors text-center group"
                  >
                    <span className="text-3xl" role="img" aria-hidden="true">{emoji}</span>
                    <span className="font-heading font-bold text-sm text-secondary-800 group-hover:text-primary-700">
                      {label}
                    </span>
                    <span className="text-xs text-secondary-400 leading-snug hidden sm:block">
                      {desc}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── Weekend events with day toggle + save + editor's pick ── */}
        <WeekendEventsSection />

        {/* ── Browse by age ── */}
        <section className="py-16 bg-primary-50/40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="font-heading font-bold text-2xl text-secondary-900 mb-8 text-center">
              Kids&apos; Events by Age Group in Northern Virginia
            </h2>
            <ul className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {AGE_GROUPS.map(({ emoji, label, sub, href }) => (
                <li key={label}>
                  <Link
                    href={href}
                    className="flex flex-col items-center gap-3 p-6 rounded-2xl bg-white border border-secondary-100 hover:border-primary-300 hover:shadow-md transition-all group text-center"
                  >
                    <span className="text-4xl" role="img" aria-hidden="true">{emoji}</span>
                    <div>
                      <p className="font-heading font-bold text-sm text-secondary-900 group-hover:text-primary-700 transition-colors">
                        {label}
                      </p>
                      <p className="text-xs text-secondary-400 mt-0.5">{sub}</p>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── Free events spotlight ── */}
        <FreeEventsSection />

        {/* ── Events by city ── */}
        <CityStripsSection />

        {/* ── Blog / editorial ── */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
              <h2 className="font-heading font-bold text-2xl text-secondary-900">
                NoVa Family Activity Guides
              </h2>
              <Link
                href="/blog"
                className="text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors whitespace-nowrap"
              >
                All guides →
              </Link>
            </div>

            {livePosts.length > 0 ? (
              <ul className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                {livePosts.map((post, i) => (
                  <li key={post.slug}>
                    <Link
                      href={`/blog/${post.slug}`}
                      className={`flex flex-col h-full rounded-2xl border overflow-hidden hover:shadow-md transition-shadow group ${
                        i === 0 ? 'border-primary-200 bg-primary-50' : 'border-secondary-100 bg-white'
                      }`}
                    >
                      <div className={`flex items-center justify-center text-5xl py-10 ${
                        i === 0 ? 'bg-primary-100' : 'bg-secondary-50'
                      }`}>
                        {post.post_type === 'weekend'     ? '🗓️' :
                         post.post_type === 'free'        ? '🆓' :
                         post.post_type === 'location'    ? '📍' :
                         post.post_type === 'seasonal'    ? '🌸' :
                         post.post_type === 'week_ahead'  ? '📅' : '📖'}
                      </div>
                      <div className="p-5 flex flex-col flex-1">
                        <span className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
                          i === 0 ? 'text-primary-600' : 'text-secondary-400'
                        }`}>
                          {post.post_type?.replace('_', ' ')}
                        </span>
                        <h3 className="font-heading font-bold text-sm text-secondary-900 group-hover:text-primary-700 transition-colors leading-snug mb-2">
                          {post.title}
                        </h3>
                        {post.excerpt && (
                          <p className="text-xs text-secondary-500 leading-relaxed flex-1 line-clamp-3">
                            {post.excerpt}
                          </p>
                        )}
                        <span className="mt-4 text-xs font-semibold text-primary-600 group-hover:text-primary-700 transition-colors">
                          Read guide →
                        </span>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            ) : (
              <ul className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                {BLOG_POSTS.map(post => (
                  <li key={post.title}>
                    <Link
                      href={post.href}
                      className={`flex flex-col h-full rounded-2xl border overflow-hidden hover:shadow-md transition-shadow group ${
                        post.featured
                          ? 'border-primary-200 bg-primary-50'
                          : 'border-secondary-100 bg-white'
                      }`}
                    >
                      <div className={`flex items-center justify-center text-5xl py-10 ${
                        post.featured ? 'bg-primary-100' : 'bg-secondary-50'
                      }`}>
                        {post.emoji}
                      </div>
                      <div className="p-5 flex flex-col flex-1">
                        <span className={`text-[10px] font-bold uppercase tracking-widest mb-2 ${
                          post.featured ? 'text-primary-600' : 'text-secondary-400'
                        }`}>
                          {post.category}
                        </span>
                        <h3 className="font-heading font-bold text-sm text-secondary-900 group-hover:text-primary-700 transition-colors leading-snug mb-2">
                          {post.title}
                        </h3>
                        <p className="text-xs text-secondary-500 leading-relaxed flex-1">
                          {post.desc}
                        </p>
                        <span className="mt-4 text-xs font-semibold text-primary-600 group-hover:text-primary-700 transition-colors">
                          Read guide →
                        </span>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        {/* ── Coverage area ── */}
        <section className="py-14 bg-secondary-50">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-heading font-bold text-2xl text-secondary-900 mb-3">
              Covering All of Northern Virginia
            </h2>
            <p className="text-secondary-500 mb-7 text-sm max-w-xl mx-auto">
              From Leesburg to Woodbridge, Reston to Manassas — we track events across
              Fairfax, Loudoun, Arlington, and Prince William counties.
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
              Weekly roundup of the best events, deals, and freebies for Northern Virginia families.
              Free. No spam.
            </p>
            <NewsletterForm />
          </div>
        </section>

      </main>
    </>
  )
}
