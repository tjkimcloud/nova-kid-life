import type { Metadata } from 'next'
import Link from 'next/link'

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

// ── Category cards ───────────────────────────────────────────────────────────

const CATEGORIES = [
  { emoji: '📚', label: 'Storytime',     desc: 'Library storytimes for toddlers & kids',        href: '/events?category=storytime' },
  { emoji: '🔬', label: 'STEM',          desc: 'Science, tech & engineering workshops',          href: '/events?category=stem' },
  { emoji: '🌳', label: 'Outdoors',      desc: 'Hikes, farms, nature programs & more',          href: '/events?category=outdoor' },
  { emoji: '🎁', label: 'Free Events',   desc: 'Zero cost — just show up',                      href: '/events?free=true' },
  { emoji: '🎂', label: 'Freebies',      desc: 'Birthday freebies & restaurant deals',          href: '/events?category=birthday_freebie' },
  { emoji: '🃏', label: 'Pokémon TCG',   desc: 'Leagues, prereleases & tournaments in NoVa',    href: '/pokemon' },
]

const STATS = [
  { value: '59+',  label: 'Local sources' },
  { value: '4',    label: 'NoVa counties' },
  { value: 'Free', label: 'Always free' },
  { value: 'Daily', label: 'Updated' },
]

// ── Page ─────────────────────────────────────────────────────────────────────

export default function HomePage() {
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
        <section className="bg-gradient-to-b from-primary-50 to-white border-b border-primary-100">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
            <h1 className="font-heading font-extrabold text-4xl sm:text-5xl lg:text-6xl text-secondary-900 leading-tight text-balance">
              Family Events in{' '}
              <span className="text-primary-600">Northern Virginia</span>
            </h1>
            <p className="mt-5 text-lg sm:text-xl text-secondary-500 max-w-2xl mx-auto leading-relaxed text-balance">
              The most complete events calendar for NoVa families — free storytime, STEM,
              outdoor adventures, birthday freebies, and Pokémon TCG. Updated daily from
              59+ local sources.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                href="/events"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-primary-500 text-white font-semibold text-base hover:bg-primary-600 transition-colors shadow-sm"
              >
                Browse Events
                <ArrowRightIcon />
              </Link>
              <Link
                href="/events?free=true"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white text-secondary-700 font-semibold text-base hover:bg-secondary-50 transition-colors border border-secondary-200 shadow-sm"
              >
                Free Events Only
              </Link>
            </div>
          </div>
        </section>

        {/* ── Stats ── */}
        <section className="bg-secondary-900 py-8" aria-label="Site statistics">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <dl className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
              {STATS.map(({ value, label }) => (
                <div key={label}>
                  <dt className="font-heading font-extrabold text-3xl text-primary-400">
                    {value}
                  </dt>
                  <dd className="mt-1 text-sm text-secondary-400">{label}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* ── Categories ── */}
        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="font-heading font-bold text-2xl text-secondary-900 mb-8 text-center">
              What are you looking for?
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

        {/* ── Coverage ── */}
        <section className="py-16 bg-primary-50/50">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-heading font-bold text-2xl text-secondary-900 mb-4">
              Covering All of Northern Virginia
            </h2>
            <p className="text-secondary-500 mb-8 max-w-2xl mx-auto">
              From Leesburg to Woodbridge, Reston to Manassas — we track events across
              Fairfax, Loudoun, Arlington, and Prince William counties.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {[
                'Fairfax', 'Reston', 'Herndon', 'Chantilly', 'McLean',
                'Leesburg', 'Ashburn', 'Sterling', 'Manassas', 'Woodbridge',
                'Arlington', 'Alexandria', 'Vienna', 'Springfield', 'Centreville',
              ].map((city) => (
                <span
                  key={city}
                  className="px-3 py-1.5 rounded-full text-sm font-medium bg-white border border-secondary-200 text-secondary-600"
                >
                  {city}, VA
                </span>
              ))}
            </div>
            <Link
              href="/events"
              className="inline-flex items-center gap-2 mt-8 text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors"
            >
              See all upcoming events
              <ArrowRightIcon />
            </Link>
          </div>
        </section>

        {/* ── Newsletter CTA ── */}
        <section className="py-16 bg-secondary-800">
          <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="font-heading font-bold text-2xl text-white mb-3">
              Never miss a NoVa family event
            </h2>
            <p className="text-secondary-300 mb-6 text-sm">
              Weekly roundup of the best events, deals, and freebies for Northern Virginia families.
              Free. No spam.
            </p>
            <form
              action="/api/newsletter"
              method="POST"
              className="flex flex-col sm:flex-row gap-3"
              aria-label="Newsletter signup"
            >
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="your@email.com"
                className="flex-1 px-4 py-3 rounded-xl text-sm border border-secondary-600 bg-secondary-700 text-white placeholder-secondary-400 focus:outline-none focus:border-primary-400"
              />
              <button
                type="submit"
                className="px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors shrink-0"
              >
                Subscribe
              </button>
            </form>
          </div>
        </section>

      </main>
    </>
  )
}

function ArrowRightIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
    </svg>
  )
}
