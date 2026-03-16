import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About NovaKidLife — Family Events in Northern Virginia',
  description:
    'NovaKidLife aggregates family events across Fairfax, Loudoun, Arlington, and Prince William counties — updated daily from 59+ local sources. Free for Northern Virginia families.',
  alternates: { canonical: 'https://novakidlife.com/about' },
}

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">

        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-8">
          <ol className="flex items-center gap-2 text-sm text-secondary-400">
            <li><Link href="/" className="hover:text-primary-600 transition-colors">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li className="text-secondary-700 font-medium" aria-current="page">About</li>
          </ol>
        </nav>

        <h1 className="font-heading font-extrabold text-4xl text-secondary-900 mb-6">
          About NovaKidLife
        </h1>

        <div className="prose prose-secondary max-w-none text-secondary-700 leading-relaxed space-y-6">

          <p className="text-lg text-secondary-600">
            NovaKidLife is a free family events calendar for Northern Virginia — covering
            Fairfax, Loudoun, Arlington, and Prince William counties.
          </p>

          <h2 className="font-heading font-bold text-2xl text-secondary-900">Why we built this</h2>
          <p>
            Finding things to do with kids in Northern Virginia shouldn&rsquo;t be hard.
            But between county library websites, Meetup, Eventbrite, local Facebook groups,
            and dozens of venue calendars — it is. NovaKidLife pulls it all together in one
            place, updated daily, completely free.
          </p>

          <h2 className="font-heading font-bold text-2xl text-secondary-900">What we cover</h2>
          <p>
            We aggregate events from 59+ sources across Northern Virginia including:
          </p>
          <ul className="list-disc pl-6 space-y-1">
            <li>Fairfax County Public Library system (all branches)</li>
            <li>Loudoun County Public Library</li>
            <li>Arlington Public Library</li>
            <li>Eventbrite and Meetup NoVa events</li>
            <li>NOVA Parks, Reston Community Center, YMCA</li>
            <li>Local venues: Wolf Trap, Meadowlark, Cox Farms, Udvar-Hazy Center, and more</li>
            <li>Restaurant deals, birthday freebies, and family discounts</li>
            <li>Pokémon TCG leagues, prereleases, and tournaments across Northern Virginia</li>
          </ul>

          <h2 className="font-heading font-bold text-2xl text-secondary-900">Coverage area</h2>
          <p>
            We cover all of Northern Virginia with a focus on the cities and neighborhoods
            where NoVa families live: Fairfax, Reston, Herndon, Chantilly, McLean, Vienna,
            Leesburg, Ashburn, Sterling, Manassas, Woodbridge, Alexandria, Arlington,
            Springfield, Centreville, and more.
          </p>

          <h2 className="font-heading font-bold text-2xl text-secondary-900">Always free</h2>
          <p>
            NovaKidLife is and always will be free to use. No account required. No paywalls.
            We link directly to event organizers — we&rsquo;re a discovery tool, not a ticketing platform.
          </p>

          <h2 className="font-heading font-bold text-2xl text-secondary-900">Contact</h2>
          <p>
            Found an event we&rsquo;re missing? Spot an error? Email us at{' '}
            <a
              href="mailto:hello@novakidlife.com"
              className="text-primary-600 hover:text-primary-700 underline"
            >
              hello@novakidlife.com
            </a>
            .
          </p>

        </div>

        <div className="mt-12 pt-8 border-t border-secondary-100">
          <Link
            href="/events"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors"
          >
            Browse Events
          </Link>
        </div>

      </div>
    </main>
  )
}
