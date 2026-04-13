import Link from 'next/link'
import type { Event } from '@/types/events'

// ── Date grouping ──────────────────────────────────────────────────────────────

function groupByDate(events: Event[]): [string, Event[]][] {
  const map = new Map<string, Event[]>()
  for (const e of events) {
    const key = e.start_at?.slice(0, 10) || 'tbd'
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(e)
  }
  return Array.from(map.entries())
}

function formatGroupLabel(dateStr: string): string {
  if (dateStr === 'tbd') return 'Date TBD'
  const today    = new Date().toISOString().slice(0, 10)
  const tomorrow = new Date(Date.now() + 86_400_000).toISOString().slice(0, 10)
  if (dateStr === today)    return 'Today'
  if (dateStr === tomorrow) return 'Tomorrow'
  // Parse in local time to avoid off-by-one from UTC conversion
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric',
  })
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString('en-US', {
      hour: 'numeric', minute: '2-digit', hour12: true,
    })
  } catch { return '' }
}

// ── Tag colour classes ────────────────────────────────────────────────────────

function tagClass(tag: string): string {
  const t = tag.toLowerCase()
  if (t.includes('free') || t.includes('outdoor') || t.includes('nature'))
    return 'bg-orange-50 text-orange-600'
  if (t.includes('stem') || t.includes('science') || t.includes('tech'))
    return 'bg-blue-50 text-blue-700'
  if (t.includes('art') || t.includes('craft') || t.includes('music'))
    return 'bg-amber-50 text-amber-700'
  if (t.includes('pokemon') || t.includes('teen'))
    return 'bg-purple-50 text-purple-700'
  if (t.includes('story') || t.includes('library') || t.includes('reading'))
    return 'bg-teal-50 text-teal-700'
  return 'bg-secondary-50 text-secondary-500'
}

// Deal event types have no meaningful time (start_at = scrape timestamp)
const DEAL_TYPES = new Set(['deal', 'birthday_freebie', 'product_drop'])

// ── Single event row ──────────────────────────────────────────────────────────

function EventRow({ event }: { event: Event }) {
  const href = event.section === 'pokemon'
    ? `/pokemon/events/${event.slug}`
    : `/events/${event.slug}`

  const isDeal   = DEAL_TYPES.has(event.event_type)
  const time     = isDeal ? null : formatTime(event.start_at)
  const location = event.location_name || 'Northern Virginia'
  const price    = event.is_free ? 'Free' : (event.cost_description || 'See details')
  const tags     = (event.tags ?? []).slice(0, 2)

  return (
    <li>
      <Link
        href={href}
        className="flex items-start gap-3 px-4 py-3.5 hover:bg-primary-50/40 transition-colors group"
      >
        {/* Time badge — hidden for deals (start_at is scrape timestamp, not event time) */}
        <span
          className="shrink-0 w-[64px] text-[11px] font-bold font-body pt-0.5 text-right leading-tight whitespace-nowrap"
          style={{ color: 'var(--orange)' }}
        >
          {time ?? ''}
        </span>

        {/* Title + meta */}
        <div className="flex-1 min-w-0">
          <p className="font-heading font-semibold text-[14px] leading-snug text-secondary-900 group-hover:text-primary-600 transition-colors line-clamp-2 mb-1">
            {event.title}
          </p>
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] text-secondary-400 font-body truncate max-w-[180px]">
              {location}
            </span>
            {tags.map(tag => (
              <span
                key={tag}
                className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full leading-none ${tagClass(tag)}`}
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Price + chevron */}
        <div className="shrink-0 flex items-center gap-1.5">
          <span className={`text-[11px] font-bold font-body whitespace-nowrap ${
            event.is_free ? '' : 'text-secondary-500'
          }`} style={event.is_free ? { color: 'var(--orange)' } : {}}>
            {event.is_free ? '🆓 Free' : price}
          </span>
          <svg
            className="w-3.5 h-3.5 text-secondary-300 group-hover:text-primary-400 transition-colors shrink-0"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </Link>
    </li>
  )
}

// ── Exported grid (now a date-grouped list) ───────────────────────────────────

interface EventGridProps {
  events: Event[]
}

export function EventGrid({ events }: EventGridProps) {
  const groups = groupByDate(events)

  return (
    <div className="space-y-4">
      {groups.map(([dateStr, groupEvents]) => (
        <div
          key={dateStr}
          className="overflow-hidden border border-secondary-100 bg-white"
          style={{ borderRadius: 'var(--radius-lg)', boxShadow: 'var(--shadow-sm)' }}
        >
          {/* Date section header */}
          <div className="px-4 py-2.5 border-b border-secondary-100 flex items-center justify-between"
            style={{ background: 'var(--bg)' }}>
            <h3 className="font-heading font-bold text-[12px] uppercase tracking-widest text-secondary-500">
              {formatGroupLabel(dateStr)}
            </h3>
            <span className="text-[11px] text-secondary-400 font-body">
              {groupEvents.length} event{groupEvents.length !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Event rows */}
          <ul className="divide-y divide-secondary-50">
            {groupEvents.map(event => (
              <EventRow key={event.id} event={event} />
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
