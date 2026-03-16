import Link from 'next/link'
import { BlurImage } from './BlurImage'
import type { Event } from '@/types/events'

interface EventCardProps {
  event: Event
  priority?: boolean
}

function formatEventDate(startAt: string): { date: string; time: string } {
  const d = new Date(startAt)
  const date = d.toLocaleDateString('en-US', {
    weekday: 'short',
    month:   'short',
    day:     'numeric',
  }).toUpperCase()
  const time = d.toLocaleTimeString('en-US', {
    hour:   'numeric',
    minute: '2-digit',
  })
  return { date, time }
}

function CostBadge({ event }: { event: Event }) {
  if (event.is_free) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-secondary-100 text-secondary-800">
        FREE
      </span>
    )
  }
  if (event.cost_description) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-primary-100 text-primary-800">
        {event.cost_description}
      </span>
    )
  }
  return null
}

function PinIcon() {
  return (
    <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M9.69 18.933l.003.001C9.89 19.02 10 19 10 19s.11.02.308-.066l.002-.001.006-.003.018-.008a5.741 5.741 0 00.281-.14c.186-.096.446-.24.757-.433.62-.384 1.445-.966 2.274-1.765C15.302 15.027 17 12.49 17 9A7 7 0 103 9c0 3.49 1.698 6.027 3.354 7.584a13.731 13.731 0 002.273 1.765 11.842 11.842 0 00.976.544l.062.029.018.008.006.003zM10 11.25a2.25 2.25 0 100-4.5 2.25 2.25 0 000 4.5z" clipRule="evenodd" />
    </svg>
  )
}

export function EventCard({ event, priority = false }: EventCardProps) {
  const { date, time } = formatEventDate(event.start_at)
  const href = event.section === 'pokemon'
    ? `/pokemon/events/${event.slug}`
    : `/events/${event.slug}`

  const visibleTags = event.tags.slice(0, 3)

  return (
    <article className="group flex flex-col rounded-2xl overflow-hidden bg-white shadow-sm border border-secondary-100 hover:shadow-md transition-shadow duration-200">
      {/* Image */}
      <Link href={href} className="block" tabIndex={-1} aria-hidden="true">
        <BlurImage
          src={event.image_url}
          lqip={event.image_blurhash ? undefined : null}
          alt={event.image_alt ?? event.title}
          width={600}
          height={400}
          className="w-full"
          priority={priority}
        />
      </Link>

      {/* Content */}
      <div className="flex flex-col flex-1 p-4 gap-2">
        {/* Date + cost badge */}
        <div className="flex items-center justify-between gap-2">
          <time
            dateTime={event.start_at}
            className="text-xs font-semibold tracking-wide text-primary-600"
          >
            {date} · {time}
          </time>
          <CostBadge event={event} />
        </div>

        {/* Title */}
        <Link href={href} className="group/title">
          <h2 className="font-heading font-bold text-base leading-snug text-secondary-900 line-clamp-2 group-hover/title:text-primary-700 transition-colors">
            {event.title}
          </h2>
        </Link>

        {/* Location */}
        {event.location_name && (
          <div className="flex items-center gap-1 text-secondary-500 text-sm">
            <PinIcon />
            <span className="truncate">{event.location_name}</span>
          </div>
        )}

        {/* Tags */}
        {visibleTags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-auto pt-2">
            {visibleTags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-primary-50 text-primary-700 border border-primary-100"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  )
}
