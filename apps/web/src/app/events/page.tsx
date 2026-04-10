import { Suspense } from 'react'
import type { Metadata } from 'next'
import { EventsClient } from './EventsClient'
import { EventGridSkeleton } from '@/components/EventCardSkeleton'

const ITEM_LIST_SCHEMA = {
  '@context':   'https://schema.org',
  '@type':      'ItemList',
  name:          'Family Events in Northern Virginia',
  description:   'Upcoming family events and kids activities in Northern Virginia',
  url:           'https://novakidlife.com/events',
  areaServed: {
    '@type':     'State',
    name:        'Virginia',
  },
}

export const metadata: Metadata = {
  title: 'Family Events in Northern Virginia',
  description:
    'Family events and kids activities in Northern Virginia — Fairfax, Loudoun, Arlington, Prince William. Updated daily from 50+ local sources.',
  openGraph: {
    title:       'Family Events in Northern Virginia | NovaKidLife',
    description: 'Find the best family events, kids activities, and things to do in Northern Virginia this week.',
    type:        'website',
    images: [{
      url:    'https://novakidlife.com/images/hero-family-meadow-v2.jpg',
      width:  1200,
      height: 630,
      alt:    'Family enjoying outdoor activities in Northern Virginia',
    }],
  },
  alternates: {
    canonical: 'https://novakidlife.com/events',
  },
}

export default function EventsPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(ITEM_LIST_SCHEMA) }}
      />
    <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
      {/* Page header */}
      <div className="bg-white border-b border-secondary-100">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
          <h1 className="font-heading font-extrabold text-2xl sm:text-3xl" style={{ color: 'var(--text)' }}>
            Family Events &amp; Deals —{' '}
            <span style={{ color: 'var(--orange)' }}>Northern Virginia</span>
          </h1>
          <p className="mt-1.5 text-sm max-w-xl" style={{ color: 'var(--text2)' }}>
            Local events for kids and families across Fairfax, Loudoun, Arlington, and Prince William — plus birthday freebies and family deals.
          </p>
        </div>
      </div>

      {/* Main content — narrower max-width for list readability */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
        <Suspense fallback={<EventGridSkeleton count={12} />}>
          <EventsClient />
        </Suspense>
      </div>
    </main>
    </>
  )
}
