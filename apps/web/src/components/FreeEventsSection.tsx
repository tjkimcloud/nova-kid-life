'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

type FreeEvent = {
  title:    string
  date:     string
  location: string
  tags:     string[]
  href:     string
}

type ApiEvent = {
  id:               string
  slug:             string
  title:            string
  start_at:         string
  location_name:    string
  location_address?: string
  is_free:          boolean
  tags?:            string[]
}

function formatDateShort(iso: string): string {
  try {
    const d = new Date(iso)
    const datePart = d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    const timePart = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
    return `${datePart} · ${timePart}`
  } catch {
    return ''
  }
}

function apiToFreeEvent(e: ApiEvent): FreeEvent {
  return {
    title:    e.title,
    date:     e.start_at ? formatDateShort(e.start_at) : 'TBD',
    location: e.location_name || e.location_address || 'Northern Virginia',
    tags:     e.tags?.slice(0, 2) || [],
    href:     `/events/${e.slug}`,
  }
}

export function FreeEventsSection() {
  const [events,  setEvents]  = useState<FreeEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const now = new Date().toISOString().slice(0, 10)
    const base = process.env.NEXT_PUBLIC_API_URL || 'https://api.novakidlife.com'
    const url = `${base}/events?is_free=true&start_date=${now}&limit=4&section=main`

    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(r => r.json())
      .then((data: { items?: ApiEvent[] }) => {
        setEvents((data.items || []).map(apiToFreeEvent))
        setLoading(false)
      })
      .catch(() => setLoading(false))

    return () => controller.abort()
  }, [])

  return (
    <section className="py-16" style={{ background: 'var(--bg)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide mb-3" style={{ background: 'var(--orange-pale)', color: 'var(--orange)' }}>
              🆓 Zero Cost
            </span>
            <h2 className="font-heading font-bold text-2xl" style={{ color: 'var(--text)' }}>
              Free Things To Do With Kids in Northern Virginia This Weekend
            </h2>
          </div>
          <Link
            href="/events?free=true"
            className="shrink-0 inline-flex items-center gap-1.5 text-sm font-semibold transition-colors whitespace-nowrap"
            style={{ color: 'var(--orange)' }}
          >
            See all free events
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>

        {loading ? (
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[0, 1, 2, 3].map(i => (
              <li key={i} className="flex items-start gap-4 p-4 rounded-2xl bg-white border border-secondary-100 animate-pulse">
                <div className="flex-shrink-0 w-10 h-10 rounded-xl" style={{ background: 'var(--orange-pale)' }} />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 rounded bg-secondary-100" />
                  <div className="h-3 w-1/2 rounded bg-secondary-100" />
                </div>
              </li>
            ))}
          </ul>
        ) : events.length > 0 ? (
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {events.map(event => (
              <li key={event.title}>
                <Link
                  href={event.href}
                  className="flex items-start gap-4 p-4 rounded-2xl bg-white border border-secondary-100 hover:shadow-sm transition-all group"
                  style={{ borderColor: 'var(--border)' }}
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: 'var(--orange-pale)' }}>
                    <span className="text-lg" aria-hidden="true">🆓</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-heading font-bold text-sm text-secondary-900 group-hover:text-primary-700 transition-colors leading-snug mb-1 line-clamp-2">
                      {event.title}
                    </p>
                    <p className="text-xs text-secondary-400">{event.date} · {event.location}</p>
                    <div className="flex flex-wrap gap-1 mt-1.5">
                      {event.tags.map(tag => (
                        <span key={tag} className="px-2 py-0.5 rounded-full bg-secondary-50 text-secondary-400 text-[10px] font-semibold">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-secondary-300 group-hover:text-primary-500 shrink-0 mt-0.5 transition-colors" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                  </svg>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-center text-secondary-400 py-8 text-sm">
            Free events are being added — check back soon.
          </p>
        )}

        <p className="mt-6 text-center text-sm text-secondary-400">
          All events above are 100% free — no registration required unless noted.
        </p>

      </div>
    </section>
  )
}
