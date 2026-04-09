import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Pokémon TCG Events in Northern Virginia',
  description:
    'Pokémon TCG leagues, prereleases, regional championships, and product drops in Northern Virginia. Find events at Nerd Rage Gaming, Battlegrounds, The Game Parlor, and more NoVa game stores.',
  alternates: { canonical: 'https://novakidlife.com/pokemon' },
  openGraph: {
    title:       'Pokémon TCG Events in Northern Virginia | NovaKidLife',
    description: 'Pokémon TCG leagues, prereleases, and tournaments across Fairfax, Loudoun, Arlington, and Prince William counties.',
    type:        'website',
    images: [{
      url:    'https://novakidlife.com/images/hero-family-meadow-v2.jpg',
      width:  1200,
      height: 630,
      alt:    'Family enjoying outdoor activities in Northern Virginia',
    }],
  },
}

const POKEMON_SCHEMA = {
  '@context':   'https://schema.org',
  '@type':      'ItemList',
  name:          'Pokémon TCG Events in Northern Virginia',
  description:   'Pokémon TCG leagues, prereleases, and tournaments in Northern Virginia',
  url:           'https://novakidlife.com/pokemon',
  areaServed: {
    '@type': 'State',
    name:    'Virginia',
  },
}

const EVENT_TYPES = [
  { emoji: '🏆', label: 'League Nights',     desc: 'Weekly structured play at local game stores', href: '/pokemon/events?format=league' },
  { emoji: '🎴', label: 'Prereleases',        desc: 'Be first to play new TCG sets',              href: '/pokemon/events?format=prerelease' },
  { emoji: '🥇', label: 'Regional Champs',   desc: 'Competitive tournaments and regionals',       href: '/pokemon/events?format=regional' },
  { emoji: '📦', label: 'Product Drops',     desc: 'New set release dates and where to buy',     href: '/pokemon/drops' },
]

const LGS = [
  { name: 'Nerd Rage Gaming',   city: 'Manassas' },
  { name: 'Battlegrounds',      city: 'Leesburg / Ashburn' },
  { name: 'The Game Parlor',    city: 'Chantilly' },
  { name: "Collector's Cache",  city: 'Alexandria' },
  { name: 'Dream Wizards',      city: 'Rockville, MD' },
]

export default function PokemonHubPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(POKEMON_SCHEMA) }}
      />

      <main className="min-h-screen bg-primary-50/30">

        {/* Hero */}
        <div className="bg-white border-b border-secondary-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
            <nav aria-label="Breadcrumb" className="mb-4">
              <ol className="flex items-center gap-2 text-sm text-secondary-400">
                <li><Link href="/" className="hover:text-primary-600 transition-colors">Home</Link></li>
                <li aria-hidden="true">/</li>
                <li className="text-secondary-700 font-medium" aria-current="page">Pokémon TCG</li>
              </ol>
            </nav>
            <h1 className="font-heading font-extrabold text-3xl sm:text-4xl text-secondary-900">
              Pokémon TCG in{' '}
              <span className="text-primary-600">Northern Virginia</span>
            </h1>
            <p className="mt-2 text-secondary-500 text-base max-w-2xl">
              Leagues, prereleases, regional championships, and new set releases across NoVa.
              Updated daily from 5 local game stores and the Play! Pokémon event locator.
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">

          {/* Event types */}
          <section>
            <h2 className="font-heading font-bold text-xl text-secondary-900 mb-5">
              Find Your Event
            </h2>
            <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {EVENT_TYPES.map(({ emoji, label, desc, href }) => (
                <li key={label}>
                  <Link
                    href={href}
                    className="flex flex-col gap-3 p-6 rounded-2xl bg-white border border-secondary-100 hover:border-primary-200 hover:bg-primary-50 transition-colors group"
                  >
                    <span className="text-3xl" role="img" aria-hidden="true">{emoji}</span>
                    <div>
                      <p className="font-heading font-bold text-secondary-800 group-hover:text-primary-700">
                        {label}
                      </p>
                      <p className="text-sm text-secondary-400 mt-0.5">{desc}</p>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          </section>

          {/* Local game stores */}
          <section>
            <h2 className="font-heading font-bold text-xl text-secondary-900 mb-2">
              NoVa Local Game Stores
            </h2>
            <p className="text-secondary-500 text-sm mb-5">
              These are the primary venues hosting Pokémon TCG events across Northern Virginia.
            </p>
            <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {LGS.map(({ name, city }) => (
                <li
                  key={name}
                  className="flex items-center gap-3 p-4 rounded-xl bg-white border border-secondary-100"
                >
                  <span className="text-2xl" aria-hidden="true">🃏</span>
                  <div>
                    <p className="font-semibold text-secondary-800 text-sm">{name}</p>
                    <p className="text-xs text-secondary-400">{city}, VA</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          {/* CTA */}
          <section className="bg-white rounded-2xl border border-secondary-100 p-8 text-center">
            <h2 className="font-heading font-bold text-xl text-secondary-900 mb-2">
              Where to Buy Pokémon Cards in Northern Virginia
            </h2>
            <p className="text-secondary-500 text-sm mb-6 max-w-lg mx-auto">
              From Target and Walmart to specialty game stores — our retailer guide covers
              every place to find Pokémon TCG products across NoVa.
            </p>
            <Link
              href="/pokemon/drops"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors"
            >
              View NoVa Retailer Guide
            </Link>
          </section>

        </div>
      </main>
    </>
  )
}
