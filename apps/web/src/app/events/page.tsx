import { Suspense } from 'react'
import type { Metadata } from 'next'
import { EventsClient } from './EventsClient'
import { EventGridSkeleton } from '@/components/EventCardSkeleton'

export const metadata: Metadata = {
  title: 'Family Events in Northern Virginia',
  description:
    'Family events and kids activities in Northern Virginia — Fairfax, Loudoun, Arlington, Prince William. Updated daily from 50+ local sources.',
  openGraph: {
    title:       'Family Events in Northern Virginia | NovaKidLife',
    description: 'Find the best family events, kids activities, and things to do in Northern Virginia this week.',
    type:        'website',
  },
  alternates: {
    canonical: 'https://novakidlife.com/events',
  },
}

export default function EventsPage() {
  return (
    <main className="min-h-screen bg-primary-50/30">
      {/* Page header */}
      <div className="bg-white border-b border-secondary-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <h1 className="font-heading font-extrabold text-3xl sm:text-4xl text-secondary-900">
            Family Events in{' '}
            <span className="text-primary-600">Northern Virginia</span>
          </h1>
          <p className="mt-2 text-secondary-500 text-base max-w-2xl">
            Discover things to do with your kids — from storytime and sports to festivals,
            STEM, and deals. Updated daily from 50+ local sources.
          </p>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Suspense fallback={<EventGridSkeleton count={12} />}>
          <EventsClient />
        </Suspense>
      </div>
    </main>
  )
}
