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

type DayTab = {
  dateStr:  string   // YYYY-MM-DD
  label:    string   // "Today", "Tomorrow", "Fri", etc.
  fullLabel: string  // "Friday, Mar 28"
}

function getNext7Days(): DayTab[] {
  const days: DayTab[] = []
  const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const now = new Date()
  for (let i = 0; i < 7; i++) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i)
    const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    const label = i === 0 ? 'Today' : i === 1 ? 'Tomorrow' : DAY_NAMES[d.getDay()]
    const fullLabel = `${DAY_NAMES[d.getDay()]}, ${MONTH_NAMES[d.getMonth()]} ${d.getDate()}`
    days.push({ dateStr, label, fullLabel })
  }
  return days
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
  const [days]              = useState<DayTab[]>(() => getNext7Days())
  const [activeDay, setActiveDay] = useState<string>(() => getNext7Days()[0].dateStr)
  const [saved,     setSaved]     = useState<Set<string>>(new Set())
  const [eventsByDay, setEventsByDay] = useState<Record<string, EventStub[]>>({})
  const [loading,   setLoading]   = useState(true)

  useEffect(() => {
    const todayStr = days[0].dateStr
    const lastStr  = days[days.length - 1].dateStr
    const endStr   = `${lastStr}T23:59:59`
    const base = process.env.NEXT_PUBLIC_API_URL || 'https://api.novakidlife.com'
    const url = `${base}/events?start_date=${todayStr}&end_date=${endStr}&limit=50&section=main`

    const controller = new AbortController()
    fetch(url, { signal: controller.signal })
      .then(r => r.json())
      .then((data: { items?: ApiEvent[] }) => {
        const items = data.items || []
        const grouped: Record<string, EventStub[]> = {}
        for (const day of days) {
          const dayItems = items
            .filter(e => e.start_at?.startsWith(day.dateStr))
            .slice(0, 3)
            .map(e => apiToStub(e, day.fullLabel))
          grouped[day.dateStr] = dayItems
        }
        setEventsByDay(grouped)
        setLoading(false)
      })
      .catch(() => setLoading(false))

    return () => controller.abort()
  }, [days])

  const activeEvents = eventsByDay[activeDay] || []

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

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h2 className="font-heading font-bold text-2xl text-secondary-900">
            Upcoming Events This Week
          </h2>
        </div>

        {/* Day tabs — horizontally scrollable on mobile */}
        <div className="flex gap-1 overflow-x-auto pb-2 mb-6 scrollbar-none">
          {days.map((day) => {
            const count = eventsByDay[day.dateStr]?.length ?? 0
            const isActive = activeDay === day.dateStr
            return (
              <button
                key={day.dateStr}
                onClick={() => setActiveDay(day.dateStr)}
                className={`flex-none flex flex-col items-center px-4 py-2 rounded-xl text-sm font-semibold transition-colors whitespace-nowrap ${
                  isActive
                    ? 'bg-primary-500 text-white'
                    : 'bg-secondary-50 text-secondary-600 hover:bg-secondary-100'
                }`}
              >
                <span>{day.label}</span>
                {!loading && count > 0 && (
                  <span className={`text-[10px] font-bold mt-0.5 ${isActive ? 'text-primary-100' : 'text-primary-500'}`}>
                    {count} event{count !== 1 ? 's' : ''}
                  </span>
                )}
              </button>
            )
          })}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {loading ? (
            <>
              <CardSkeleton />
              <CardSkeleton />
              <CardSkeleton />
            </>
          ) : activeEvents.length > 0 ? (
            activeEvents.map(event => (
              <EventStubCard
                key={event.id}
                event={event}
                saved={saved.has(event.id)}
                onSave={() => toggleSave(event.id)}
              />
            ))
          ) : (
            <p className="col-span-3 text-center text-secondary-400 py-8 text-sm">
              No events found for this day — check another day or browse all events.
            </p>
          )}
        </div>

        <div className="mt-8 text-center">
          <Link
            href="/events"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-secondary-200 text-sm font-semibold text-secondary-700 hover:border-primary-300 hover:text-primary-700 transition-colors"
          >
            See all upcoming events
            <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
            </svg>
          </Link>
        </div>

      </div>
    </section>
  )
}
