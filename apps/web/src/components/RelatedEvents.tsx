'use client'

import { useEffect, useState } from 'react'
import { getEvents } from '@/lib/api'
import type { Event } from '@/types/events'
import { EventCard } from './EventCard'
import { EventCardSkeleton } from './EventCardSkeleton'

interface Props {
  currentSlug: string
  section: 'main' | 'pokemon'
  tags: string[]
}

export function RelatedEvents({ currentSlug, section, tags }: Props) {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const tagsParam = tags.slice(0, 3).join(',')
    getEvents({
      section,
      tags: tagsParam || undefined,
      limit: 4,
      offset: 0,
    })
      .then((resp) => {
        const filtered = resp.items.filter((e) => e.slug !== currentSlug).slice(0, 3)
        setEvents(filtered)
      })
      .catch(() => setEvents([]))
      .finally(() => setLoading(false))
  }, [currentSlug, section, tags])

  if (!loading && events.length === 0) return null

  return (
    <section aria-labelledby="related-heading">
      <h2
        id="related-heading"
        className="font-heading font-bold text-xl text-secondary-900 mb-4"
      >
        Similar Events Near You
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading
          ? Array.from({ length: 3 }).map((_, i) => <EventCardSkeleton key={i} />)
          : events.map((event) => (
              <article key={event.slug}>
                <h3 className="sr-only">{event.title}</h3>
                <EventCard event={event} />
              </article>
            ))}
      </div>
    </section>
  )
}
