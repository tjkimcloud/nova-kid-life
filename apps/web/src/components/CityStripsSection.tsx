'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

type CityEvent = {
  title: string
  date:  string
  cost:  string
  href:  string
}

type CityStrip = {
  city:        string
  slug:        string
  emoji:       string
  description: string
  events:      CityEvent[]
}

type ApiEvent = {
  id:               string
  slug:             string
  title:            string
  start_at:         string
  location_name:    string
  location_address?: string
  is_free:          boolean
  cost_description?: string
}

const CITY_META = [
  { city: 'Reston',    slug: 'Reston',    emoji: '🌳', description: 'Nature walks, community center events & more' },
  { city: 'Fairfax',   slug: 'Fairfax',   emoji: '🏛️', description: 'Library programs, parks & cultural events' },
  { city: 'Arlington', slug: 'Arlington', emoji: '🌆', description: 'Urban adventures, museums & family dining' },
  { city: 'Leesburg',  slug: 'Leesburg',  emoji: '🌾', description: 'Historic downtown, farms & Loudoun events' },
]

function formatDateShort(iso: string): string {
  try {
    const d = new Date(iso)
    const day  = d.toLocaleDateString('en-US', { weekday: 'short' })
    const time = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
    return `${day} · ${time}`
  } catch {
    return ''
  }
}

function matchesCity(e: ApiEvent, city: string): boolean {
  const loc = `${e.location_name || ''} ${e.location_address || ''}`.toLowerCase()
  const c   = city.toLowerCase()
  // Match on location fields (primary) or title containing city name
  return loc.includes(c) || (e.title || '').toLowerCase().includes(c)
}

function CityCard({ strip }: { strip: CityStrip }) {
  return (
    <div className="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden">
      <div className="px-5 py-4 border-b border-secondary-50 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="text-2xl" aria-hidden="true">{strip.emoji}</span>
          <div>
            <h3 className="font-heading font-bold text-base text-secondary-900">{strip.city}, VA</h3>
            <p className="text-xs text-secondary-400">{strip.description}</p>
          </div>
        </div>
      </div>

      <ul className="divide-y divide-secondary-50">
        {strip.events.length > 0 ? strip.events.map(event => (
          <li key={event.href + event.title}>
            <Link
              href={event.href}
              className="flex items-center justify-between px-5 py-3 hover:bg-secondary-50 transition-colors group"
            >
              <div>
                <p className="text-sm font-semibold text-secondary-800 group-hover:text-primary-700 transition-colors leading-snug">
                  {event.title}
                </p>
                <p className="text-xs text-secondary-400 mt-0.5">{event.date}</p>
              </div>
              <span className={`text-xs font-bold shrink-0 ml-3 ${event.cost === 'Free' ? 'text-green-600' : 'text-secondary-500'}`}>
                {event.cost === 'Free' ? '🆓 Free' : event.cost}
              </span>
            </Link>
          </li>
        )) : (
          <li className="px-5 py-4 text-xs text-secondary-400">
            Events loading — check back soon.
          </li>
        )}
      </ul>

      <div className="px-5 py-3 bg-secondary-50/50">
        <Link
          href={`/events?q=${strip.slug}`}
          className="text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors"
        >
          See all events in {strip.city} →
        </Link>
      </div>
    </div>
  )
}

export function CityStripsSection() {
  const [strips,  setStrips]  = useState<CityStrip[]>(CITY_META.map(m => ({ ...m, events: [] })))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const now = new Date().toISOString().slice(0, 10)
    const base = process.env.NEXT_PUBLIC_API_URL || 'https://api.novakidlife.com'
    const url = `${base}/events?start_date=${now}&limit=100&section=main`

    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(r => r.json())
      .then((data: { items?: ApiEvent[] }) => {
        const items = data.items || []
        setStrips(CITY_META.map(meta => ({
          ...meta,
          events: items
            .filter(e => matchesCity(e, meta.city))
            .slice(0, 2)
            .map(e => ({
              title: e.title,
              date:  e.start_at ? formatDateShort(e.start_at) : 'TBD',
              cost:  e.is_free ? 'Free' : (e.cost_description || 'See event'),
              href:  `/events/${e.slug}`,
            })),
        })))
        setLoading(false)
      })
      .catch(() => setLoading(false))

    return () => controller.abort()
  }, [])

  return (
    <section className="py-16 bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-10">
          <h2 className="font-heading font-bold text-2xl text-secondary-900">
            Family Events Near You — by City
          </h2>
          <p className="mt-2 text-secondary-500 text-sm">
            Fairfax · Loudoun · Arlington · Prince William counties
          </p>
        </div>

        <div className={`grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 ${loading ? 'opacity-60 animate-pulse' : ''}`}>
          {strips.map(strip => (
            <CityCard key={strip.city} strip={strip} />
          ))}
        </div>

        <div className="mt-8 text-center">
          <Link
            href="/events"
            className="inline-flex items-center gap-2 text-sm font-semibold text-secondary-500 hover:text-secondary-700 transition-colors"
          >
            Browse all Northern Virginia events
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>

      </div>
    </section>
  )
}
