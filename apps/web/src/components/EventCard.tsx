import Link from 'next/link'
import { BlurImage } from './BlurImage'
import type { Event } from '@/types/events'

interface EventCardProps {
  event:    Event
  priority?: boolean
}

function formatEventDate(startAt: string): { date: string; time: string } {
  const d    = new Date(startAt)
  const date = d.toLocaleDateString('en-US', {
    weekday: 'short', month: 'short', day: 'numeric',
  }).toUpperCase()
  const time = d.toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit',
  })
  return { date, time }
}

function tagClass(tag: string): string {
  const t = tag.toLowerCase()
  if (t.includes('free') || t.includes('outdoor') || t.includes('nature')) return 'tag tag-g'
  if (t.includes('stem') || t.includes('science') || t.includes('tech'))   return 'tag tag-b'
  if (t.includes('art') || t.includes('craft') || t.includes('music'))     return 'tag tag-y'
  if (t.includes('pokemon') || t.includes('teen') || t.includes('age'))    return 'tag tag-p'
  return 'tag tag-o'
}

function PinIcon() {
  return (
    <svg className="w-3 h-3 shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
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
    <article
      className="group flex flex-col overflow-hidden bg-white border border-secondary-200 transition-all duration-200 hover:-translate-y-0.5"
      style={{ borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)' }}
      onMouseEnter={undefined}
    >
      {/* Image */}
      <Link href={href} tabIndex={-1} aria-hidden="true" className="block overflow-hidden">
        <BlurImage
          src={event.image_url}
          lqip={event.image_blurhash ? undefined : null}
          alt={event.image_alt ?? event.title}
          width={600}
          height={400}
          className="w-full transition-transform duration-500 group-hover:scale-[1.03]"
          priority={priority}
        />
      </Link>

      {/* Card body */}
      <div className="flex flex-col flex-1 p-[15px] gap-2">
        {/* Tags */}
        {visibleTags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {visibleTags.map((tag) => (
              <span key={tag} className={tagClass(tag)}>{tag}</span>
            ))}
          </div>
        )}

        {/* Title */}
        <Link href={href}>
          <h2
            className="font-heading font-bold text-[15px] leading-snug line-clamp-2 transition-colors"
            style={{ color: 'var(--text)', letterSpacing: '-0.1px' }}
          >
            {event.title}
          </h2>
        </Link>

        {/* Description */}
        {event.description && (
          <p className="font-body text-[13px] leading-relaxed line-clamp-2" style={{ color: 'var(--text2)' }}>
            {event.description}
          </p>
        )}

        {/* Date + location */}
        <div className="flex flex-col gap-1 mt-auto pt-1">
          <time
            dateTime={event.start_at}
            className="font-body text-[11px] font-semibold tracking-wide"
            style={{ color: 'var(--orange)' }}
          >
            {date} · {time}
          </time>
          {event.location_name && (
            <div className="flex items-center gap-1 font-body text-[12px]" style={{ color: 'var(--text3)' }}>
              <PinIcon />
              <span className="truncate">{event.location_name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Card footer — price + CTA */}
      <div
        className="flex items-center justify-between px-4 py-[11px] border-t border-secondary-200"
        style={{ background: 'var(--bg)' }}
      >
        <span className="font-body text-[12px] font-semibold" style={{ color: event.is_free ? 'var(--orange)' : 'var(--text2)' }}>
          {event.is_free ? 'FREE' : (event.cost_description || 'See details')}
        </span>
        <Link
          href={href}
          className="font-body text-[12px] font-semibold text-white px-[14px] py-[7px] transition-colors hover:opacity-90"
          style={{ background: 'var(--orange)', borderRadius: '8px' }}
        >
          Details
        </Link>
      </div>
    </article>
  )
}
