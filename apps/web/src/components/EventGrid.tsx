import { EventCard } from './EventCard'
import type { Event } from '@/types/events'

interface EventGridProps {
  events: Event[]
}

export function EventGrid({ events }: EventGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {events.map((event, i) => (
        <EventCard
          key={event.id}
          event={event}
          priority={i < 3}
        />
      ))}
    </div>
  )
}
