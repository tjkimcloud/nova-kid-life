const AMBER_WEIGHTS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950] as const
const SAGE_WEIGHTS  = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950] as const

const WEBSITE_SCHEMA = {
  '@context': 'https://schema.org',
  '@type':    'WebSite',
  name:        'NovaKidLife',
  url:         'https://novakidlife.com',
  description: 'Family events discovery platform for Northern Virginia',
  potentialAction: {
    '@type':       'SearchAction',
    target: {
      '@type':      'EntryPoint',
      urlTemplate:  'https://novakidlife.com/events?q={search_term_string}',
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
    { '@type': 'County', name: 'Fairfax County',       containedInPlace: { '@type': 'State', name: 'Virginia' } },
    { '@type': 'County', name: 'Loudoun County',       containedInPlace: { '@type': 'State', name: 'Virginia' } },
    { '@type': 'County', name: 'Arlington County',     containedInPlace: { '@type': 'State', name: 'Virginia' } },
    { '@type': 'County', name: 'Prince William County', containedInPlace: { '@type': 'State', name: 'Virginia' } },
  ],
  knowsAbout: ['Family Events', 'Kids Activities', 'Northern Virginia', 'Pokémon TCG Events'],
}

export default function HomePage() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(WEBSITE_SCHEMA) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(LOCAL_BUSINESS_SCHEMA) }} />
    <main className="min-h-screen bg-primary-50 flex flex-col items-center justify-center p-8 gap-12">

      {/* Site identity */}
      <div className="text-center">
        <h1 className="font-heading text-5xl font-extrabold text-primary-700 mb-3">
          NovaKidLife
        </h1>
        <p className="font-body text-lg text-secondary-600 font-medium">
          Family events in Northern Virginia
        </p>
      </div>

      {/* Color system swatches */}
      <div className="w-full max-w-2xl space-y-6">
        <section>
          <h2 className="font-heading font-bold text-sm uppercase tracking-wider text-stone-500 mb-2">
            Amber — Primary
          </h2>
          <div className="flex rounded-xl overflow-hidden shadow-sm">
            {AMBER_WEIGHTS.map((w) => (
              <div
                key={w}
                className="flex-1 h-12 group relative"
                style={{ backgroundColor: `var(--color-primary-${w})` }}
              >
                <span className="absolute inset-0 flex items-end justify-center pb-1 opacity-0 group-hover:opacity-100 transition-opacity text-[9px] font-mono font-bold text-black/50">
                  {w}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="font-heading font-bold text-sm uppercase tracking-wider text-stone-500 mb-2">
            Sage — Secondary
          </h2>
          <div className="flex rounded-xl overflow-hidden shadow-sm">
            {SAGE_WEIGHTS.map((w) => (
              <div
                key={w}
                className="flex-1 h-12 group relative"
                style={{ backgroundColor: `var(--color-secondary-${w})` }}
              >
                <span className="absolute inset-0 flex items-end justify-center pb-1 opacity-0 group-hover:opacity-100 transition-opacity text-[9px] font-mono font-bold text-black/50">
                  {w}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Typography preview */}
        <section className="bg-white rounded-2xl p-6 shadow-sm border border-stone-100">
          <h2 className="font-heading font-bold text-sm uppercase tracking-wider text-stone-500 mb-4">
            Typography
          </h2>
          <p className="font-heading text-4xl font-extrabold text-primary-800 mb-1">
            Nunito ExtraBold 800
          </p>
          <p className="font-heading text-2xl font-bold text-primary-700 mb-1">
            Nunito Bold 700
          </p>
          <p className="font-heading text-xl font-semibold text-primary-600 mb-4">
            Nunito SemiBold 600
          </p>
          <p className="font-body text-base font-normal text-stone-700 mb-1">
            Plus Jakarta Sans Regular 400 — Body text for event descriptions
          </p>
          <p className="font-body text-base font-medium text-stone-700 mb-1">
            Plus Jakarta Sans Medium 500 — Labels and captions
          </p>
          <p className="font-body text-base font-semibold text-stone-700">
            Plus Jakarta Sans SemiBold 600 — Emphasis and CTAs
          </p>
        </section>
      </div>

      <p className="font-body text-sm text-stone-400">
        Session 1 complete — design system ready
      </p>
    </main>
    </>
  )
}
