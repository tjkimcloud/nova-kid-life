'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

type EventStub = {
  id:       string
  title:    string
  date:     string
  time:     string
  location: string
  cost:     string
  tags:     string[]
  href:     string
  pick?:    boolean
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
  tags?:            string[]
}

function getWeekendDates(): { satStr: string; sunStr: string } {
  const now = new Date()
  const day = now.getDay() // 0=Sun, 6=Sat
  const daysToSat = day === 0 ? 6 : day === 6 ? 0 : 6 - day
  const sat = new Date(now)
  sat.setDate(now.getDate() + daysToSat)
  const sun = new Date(sat)
  sun.setDate(sat.getDate() + 1)
  const toYMD = (d: Date) => d.toISOString().slice(0, 10)
  return { satStr: toYMD(sat), sunStr: toYMD(sun) }
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
  } catch {
    return ''
  }
}

function apiToStub(e: ApiEvent, dayLabel: string): EventStub {
  return {
    id:       e.id,
    title:    e.title,
    date:     dayLabel,
    time:     e.start_at ? formatTime(e.start_at) : 'TBD',
    location: e.location_name || e.location_address || 'Northern Virginia',
    cost:     e.is_free ? 'Free' : (e.cost_description || 'See event page'),
    tags:     e.tags?.slice(0, 2) || [],
    href:     `/events/${e.slug}`,
  }
}

function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg
      className={`w-5 h-5 transition-colors ${filled ? 'text-red-500' : 'text-secondary-300 group-hover:text-red-400'}`}
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth={2}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"
      />
    </svg>
  )
}

function EventStubCard({ event, saved, onSave }: { event: EventStub; saved: boolean; onSave: () => void }) {
  const isFree = event.cost === 'Free'
  return (
    <article className="relative bg-white rounded-2xl border border-secondary-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      {event.pick && (
        <div className="absolute top-3 left-3 z-10">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-400 text-amber-900 text-[10px] font-bold uppercase tracking-wide">
            ⭐ Editor&apos;s Pick
          </span>
        </div>
      )}
      <button
        onClick={onSave}
        aria-label={saved ? 'Unsave event' : 'Save event'}
        className="group absolute top-3 right-3 z-10 w-9 h-9 flex items-center justify-center rounded-full bg-white/90 backdrop-blur-sm border border-secondary-100 shadow-sm hover:border-red-200 transition-all"
      >
        <HeartIcon filled={saved} />
      </button>

      <div className="h-2 bg-gradient-to-r from-primary-400 to-primary-600" />

      <div className="p-4">
        <div className="flex flex-wrap gap-1.5 mb-2">
          {event.tags.map(tag => (
            <span key={tag} className="px-2 py-0.5 rounded-full bg-secondary-50 text-secondary-500 text-[10px] font-semibold">
              {tag}
            </span>
          ))}
        </div>

        <h3 className="font-heading font-bold text-sm text-secondary-900 leading-snug mb-2 line-clamp-2">
          <Link href={event.href} className="hover:text-primary-700 transition-colors">
            {event.title}
          </Link>
        </h3>

        <dl className="space-y-1 text-xs text-secondary-500">
          <div className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 shrink-0 text-secondary-300" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M5.75 2a.75.75 0 01.75.75V4h7V2.75a.75.75 0 011.5 0V4h.25A2.75 2.75 0 0118 6.75v8.5A2.75 2.75 0 0115.25 18H4.75A2.75 2.75 0 012 15.25v-8.5A2.75 2.75 0 014.75 4H5V2.75A.75.75 0 015.75 2zm-1 5.5a.75.75 0 000 1.5h10.5a.75.75 0 000-1.5H4.75z" clipRule="evenodd" />
            </svg>
            <dt className="sr-only">Date &amp; time</dt>
            <dd>{event.date} · {event.time}</dd>
          </div>
          <div className="flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5 shrink-0 text-secondary-300" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M9.69 18.933l.003.001C9.89 19.02 10 19 10 19s.11.02.308-.066l.002-.001.006-.003.018-.008a5.741 5.741 0 00.281-.14c.186-.096.446-.24.757-.433.62-.384 1.445-.966 2.274-1.765C15.302 14.988 17 12.493 17 9A7 7 0 103 9c0 3.492 1.698 5.988 3.355 7.584a13.731 13.731 0 002.273 1.765 11.842 11.842 0 00.757.433l.018.008.006.003zM10 11.25a2.25 2.25 0 100-4.5 2.25 2.25 0 000 4.5z" clipRule="evenodd" />
            </svg>
            <dt className="sr-only">Location</dt>
            <dd className="truncate">{event.location}</dd>
          </div>
        </dl>

        <div className="mt-3 flex items-center justify-between">
          <span className={`text-xs font-bold ${isFree ? 'text-green-600' : 'text-secondary-700'}`}>
            {isFree ? '🆓 Free' : event.cost}
          </span>
          <Link
            href={event.href}
            className="text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors"
          >
            Details →
          </Link>
        </div>
      </div>
    </article>
  )
}

function CardSkeleton() {
  return (
    <div className="bg-white rounded-2xl border border-secondary-100 shadow-sm overflow-hidden animate-pulse">
      <div className="h-2 bg-primary-200" />
      <div className="p-4 space-y-3">
        <div className="flex gap-1.5">
          <div className="h-4 w-12 rounded-full bg-secondary-100" />
          <div className="h-4 w-16 rounded-full bg-secondary-100" />
        </div>
        <div className="h-4 w-3/4 rounded bg-secondary-100" />
        <div className="h-3 w-1/2 rounded bg-secondary-100" />
        <div className="h-3 w-2/3 rounded bg-secondary-100" />
      </div>
    </div>
  )
}

export function WeekendEventsSection() {
  const [activeDay, setActiveDay] = useState<'sat' | 'sun'>('sat')
  const [saved,     setSaved]     = useState<Set<string>>(new Set())
  const [satEvents, setSatEvents] = useState<EventStub[]>([])
  const [sunEvents, setSunEvents] = useState<EventStub[]>([])
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    const { satStr, sunStr } = getWeekendDates()
    const endStr = `${sunStr}T23:59:59`
    const base = process.env.NEXT_PUBLIC_API_URL || 'https://api.novakidlife.com'
    const url = `${base}/events?start_date=${satStr}&end_date=${endStr}&limit=12&section=main`

    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(r => r.json())
      .then((data: { items?: ApiEvent[] }) => {
        const items = data.items || []
        const sats = items
          .filter(e => e.start_at?.startsWith(satStr))
          .slice(0, 3)
          .map(e => apiToStub(e, 'Saturday'))
        const suns = items
          .filter(e => e.start_at?.startsWith(sunStr))
          .slice(0, 3)
          .map(e => apiToStub(e, 'Sunday'))
        setSatEvents(sats)
        setSunEvents(suns)
        setLoading(false)
      })
      .catch(() => setLoading(false))

    return () => controller.abort()
  }, [])

  const events = activeDay === 'sat' ? satEvents : sunEvents

  function toggleSave(id: string) {
    setSaved(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <section className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <h2 className="font-heading font-bold text-2xl text-secondary-900">
            This Weekend in Northern Virginia
          </h2>

          <div className="flex rounded-xl border border-secondary-200 overflow-hidden self-start sm:self-auto">
            {(['sat', 'sun'] as const).map((day) => (
              <button
                key={day}
                onClick={() => setActiveDay(day)}
                className={`px-5 py-2 text-sm font-semibold transition-colors ${
                  activeDay === day
                    ? 'bg-primary-500 text-white'
                    : 'bg-white text-secondary-600 hover:bg-secondary-50'
                }`}
              >
                {day === 'sat' ? 'Saturday' : 'Sunday'}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <>
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
            </>
          ) : events.length > 0 ? (
            events.map(event => (
              <EventStubCard
                key={event.id}
                event={event}
                saved={saved.has(event.id)}
                onSave={() => toggleSave(event.id)}
              />
            ))
          ) : (
            <p className="col-span-3 text-center text-secondary-400 py-8 text-sm">
              Check back soon — events are being added for this weekend.
            </p>
          )}
        </div>

        <div className="mt-8 text-center">
          <Link
            href="/events?date=weekend"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-secondary-200 text-sm font-semibold text-secondary-700 hover:border-primary-300 hover:text-primary-700 transition-colors"
          >
            See all weekend events
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>

      </div>
    </section>
  )
}
