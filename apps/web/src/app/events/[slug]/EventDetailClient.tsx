'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getEvent } from '@/lib/api'
import type { Event } from '@/types/events'
import { BlurImage }     from '@/components/BlurImage'
import { Breadcrumbs }   from '@/components/Breadcrumbs'
import { EventJsonLd, extractCity } from '@/components/EventJsonLd'
import { RelatedEvents } from '@/components/RelatedEvents'
import { ShareButtons }  from '@/components/ShareButtons'

// ── Helpers ────────────────────────────────────────────────────────────────────

function formatFullDate(startAt: string, endAt: string | null): string {
  const d = new Date(startAt)
  const opts: Intl.DateTimeFormatOptions = {
    weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
    timeZone: 'America/New_York',
  }
  const date = d.toLocaleDateString('en-US', opts)
  const timeStart = d.toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York',
  })
  if (!endAt) return `${date} · ${timeStart}`
  const timeEnd = new Date(endAt).toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York',
  })
  return `${date} · ${timeStart} – ${timeEnd}`
}

function AgeRange({ event }: { event: Event }) {
  if (event.age_min == null && event.age_max == null) return <span>All ages</span>
  if (event.age_min != null && event.age_max != null)
    return <span>Ages {event.age_min}–{event.age_max}</span>
  if (event.age_min != null) return <span>Ages {event.age_min}+</span>
  return <span>All ages</span>
}

// ── Helpers ────────────────────────────────────────────────────────────────────

const AGGREGATOR_DOMAINS = [
  'dullesmoms.com',
  'patch.com',
  'novamomsblog.com',
  'princewilliamliving.com',
  'fairfaxfamilyfun.com',
  'hipkidguide.com',
]

function isAggregatorUrl(url: string | null | undefined): boolean {
  if (!url) return false
  try {
    const host = new URL(url).hostname.replace(/^www\./, '')
    return AGGREGATOR_DOMAINS.some((d) => host === d || host.endsWith('.' + d))
  } catch {
    return false
  }
}

// ── Loading skeleton ────────────────────────────────────────────────────────────

function EventDetailSkeleton() {
  return (
    <main className="min-h-screen bg-primary-50/30">
      <div className="bg-white border-b border-secondary-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="h-4 w-48 bg-secondary-100 rounded animate-pulse" />
        </div>
      </div>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="rounded-2xl overflow-hidden bg-secondary-100 animate-pulse h-64 w-full" />
        <div className="space-y-3">
          <div className="h-8 w-3/4 bg-secondary-100 rounded animate-pulse" />
          <div className="h-4 w-1/4 bg-secondary-100 rounded animate-pulse" />
        </div>
        <div className="space-y-2">
          <div className="h-4 w-full bg-secondary-100 rounded animate-pulse" />
          <div className="h-4 w-5/6 bg-secondary-100 rounded animate-pulse" />
          <div className="h-4 w-4/6 bg-secondary-100 rounded animate-pulse" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="h-20 bg-secondary-100 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    </main>
  )
}

// ── Client component ────────────────────────────────────────────────────────────

export function EventDetailClient({ slug }: { slug: string }) {
  const [event, setEvent]   = useState<Event | null>(null)
  const [loading, setLoading] = useState(true)
  const [missing, setMissing] = useState(false)

  useEffect(() => {
    getEvent(slug)
      .then(setEvent)
      .catch(() => setMissing(true))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <EventDetailSkeleton />

  if (missing || !event) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="font-heading font-bold text-2xl text-secondary-900">Event not found</h1>
          <Link href="/events" className="text-primary-600 hover:underline text-sm">
            ← Back to all events
          </Link>
        </div>
      </main>
    )
  }

  const pageUrl = `https://novakidlife.com/events/${event.slug}`
  const city    = extractCity(event)

  return (
    <>
      <EventJsonLd event={event} />

      <main className="min-h-screen bg-primary-50/30">
        {/* Breadcrumb bar */}
        <div className="bg-white border-b border-secondary-100">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
            <Breadcrumbs
              items={[
                { name: 'Home',   href: '/' },
                { name: 'Events', href: '/events' },
                { name: event.title },
              ]}
            />
          </div>
        </div>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">

          {/* ── Hero image ── */}
          {event.image_url && (
            <div className="rounded-2xl overflow-hidden shadow-sm">
              <BlurImage
                src={event.image_url}
                lqip={event.image_blurhash ?? null}
                alt={event.image_alt ?? event.title}
                width={event.image_width ?? 1200}
                height={event.image_height ?? 675}
                className="w-full"
                priority
              />
            </div>
          )}

          {/* ── H1 + share ── */}
          <div className="flex flex-col sm:flex-row sm:items-start gap-4">
            <div className="flex-1">
              <h1 className="font-heading font-extrabold text-3xl sm:text-4xl text-secondary-900 leading-tight">
                {event.title}
              </h1>
              {event.categories?.name && (
                <p className="mt-1 text-sm text-primary-600 font-semibold">
                  {event.categories.name}
                </p>
              )}
            </div>
            <ShareButtons url={pageUrl} title={event.title} />
          </div>

          {/* ── About This Event ── */}
          <section aria-labelledby="about-heading">
            <h2
              id="about-heading"
              className="font-heading font-bold text-xl text-secondary-900 mb-3"
            >
              About This Event
            </h2>
            <div className="prose prose-secondary max-w-none text-secondary-700 leading-relaxed whitespace-pre-line">
              {event.description}
            </div>

            {event.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {event.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-50 text-primary-700 border border-primary-100"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </section>

          {/* ── Event Details ── */}
          <section aria-labelledby="details-heading">
            <h2
              id="details-heading"
              className="font-heading font-bold text-xl text-secondary-900 mb-4"
            >
              Event Details
            </h2>

            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-white rounded-xl border border-secondary-100 p-4 flex gap-3">
                <CalendarIcon />
                <div>
                  <dt className="text-xs font-semibold text-secondary-400 uppercase tracking-wide">Date &amp; Time</dt>
                  <dd className="mt-0.5 text-secondary-800 font-medium text-sm">
                    {formatFullDate(event.start_at, event.end_at)}
                  </dd>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-secondary-100 p-4 flex gap-3">
                <MapPinIcon />
                <div>
                  <dt className="text-xs font-semibold text-secondary-400 uppercase tracking-wide">Location</dt>
                  <dd className="mt-0.5 text-secondary-800 font-medium text-sm">
                    {event.location_name}
                    {event.location_address && (
                      <span className="block text-secondary-500 font-normal">{event.location_address}</span>
                    )}
                    <span className="block text-secondary-500 font-normal">{city}, VA</span>
                  </dd>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-secondary-100 p-4 flex gap-3">
                <PeopleIcon />
                <div>
                  <dt className="text-xs font-semibold text-secondary-400 uppercase tracking-wide">Age Range</dt>
                  <dd className="mt-0.5 text-secondary-800 font-medium text-sm">
                    <AgeRange event={event} />
                  </dd>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-secondary-100 p-4 flex gap-3">
                <TicketIcon />
                <div>
                  <dt className="text-xs font-semibold text-secondary-400 uppercase tracking-wide">Cost</dt>
                  <dd className="mt-0.5 text-sm">
                    {event.is_free ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-secondary-100 text-secondary-800">
                        FREE
                      </span>
                    ) : (
                      <span className="text-secondary-800 font-medium">
                        {event.cost_description ?? 'See event page for pricing'}
                      </span>
                    )}
                  </dd>
                </div>
              </div>
            </dl>

            {event.lat && event.lng && (
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${event.lat},${event.lng}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 mt-4 text-sm font-medium text-primary-600 hover:text-primary-700 transition-colors"
              >
                <MapPinIcon className="w-4 h-4" />
                View on Google Maps
              </a>
            )}
          </section>

          {/* ── CTA: Register / View Event / Original Listing ── */}
          {(() => {
            const regUrl = event.registration_url && !isAggregatorUrl(event.registration_url)
              ? event.registration_url : null
            const srcUrl = event.source_url && !isAggregatorUrl(event.source_url)
              ? event.source_url : null
            const aggUrl = event.source_url && isAggregatorUrl(event.source_url)
              ? event.source_url : null

            if (regUrl) {
              return (
                <section aria-labelledby="register-heading">
                  <h2 id="register-heading" className="font-heading font-bold text-xl text-secondary-900 mb-3">
                    How to Register
                  </h2>
                  <p className="text-secondary-600 mb-4 text-sm">
                    Spots may be limited — register early to secure your place.
                  </p>
                  <a
                    href={regUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-base hover:bg-primary-600 transition-colors shadow-sm"
                  >
                    Register Now
                    <ExternalLinkIcon />
                  </a>
                </section>
              )
            }

            if (srcUrl) {
              return (
                <section aria-labelledby="register-heading">
                  <h2 id="register-heading" className="font-heading font-bold text-xl text-secondary-900 mb-3">
                    Event Website
                  </h2>
                  <a
                    href={srcUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-base hover:bg-primary-600 transition-colors shadow-sm"
                  >
                    View Event Details
                    <ExternalLinkIcon />
                  </a>
                </section>
              )
            }

            if (aggUrl) {
              return (
                <p className="text-sm text-secondary-500">
                  <a
                    href={aggUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline hover:text-secondary-700 inline-flex items-center gap-1"
                  >
                    View original listing
                    <ExternalLinkIcon />
                  </a>
                </p>
              )
            }

            return null
          })()}

          {/* ── FAQ ── */}
          <section aria-labelledby="faq-heading" className="bg-white rounded-2xl border border-secondary-100 p-6">
            <h2
              id="faq-heading"
              className="font-heading font-bold text-xl text-secondary-900 mb-4"
            >
              Frequently Asked Questions
            </h2>
            <dl className="space-y-4">
              <div>
                <dt className="font-semibold text-secondary-800">Is {event.title} free?</dt>
                <dd className="mt-1 text-secondary-600 text-sm">
                  {event.is_free
                    ? `Yes, ${event.title} is free to attend.`
                    : `${event.title} costs ${event.cost_description ?? 'an admission fee'}.`}
                </dd>
              </div>
              <div>
                <dt className="font-semibold text-secondary-800">Where is {event.title} held?</dt>
                <dd className="mt-1 text-secondary-600 text-sm">
                  {event.title} is held at {event.location_name} in {city}, Virginia.
                  {event.location_address && ` The address is ${event.location_address}.`}
                </dd>
              </div>
              <div>
                <dt className="font-semibold text-secondary-800">What ages is {event.title} for?</dt>
                <dd className="mt-1 text-secondary-600 text-sm">
                  {event.age_min != null && event.age_max != null
                    ? `${event.title} is for children ages ${event.age_min}–${event.age_max}.`
                    : event.age_min != null
                    ? `${event.title} is for children ages ${event.age_min} and up.`
                    : 'All ages are welcome.'}
                </dd>
              </div>
              <div>
                <dt className="font-semibold text-secondary-800">How do I attend {event.title}?</dt>
                <dd className="mt-1 text-secondary-600 text-sm">
                  {event.registration_url
                    ? `Register online in advance at the link above. Spots may be limited.`
                    : `No registration required — just show up at ${event.location_name} on the day of the event.`}
                </dd>
              </div>
            </dl>
          </section>

          {/* ── Related Events ── */}
          <RelatedEvents
            currentSlug={event.slug}
            section={event.section}
            tags={event.tags}
          />

          {/* ── Back to listing ── */}
          <div className="pt-2">
            <Link
              href="/events"
              className="inline-flex items-center gap-2 text-sm font-medium text-secondary-500 hover:text-primary-600 transition-colors"
            >
              <BackArrowIcon />
              Back to all events
            </Link>
          </div>

        </div>
      </main>
    </>
  )
}

// ── Icons ───────────────────────────────────────────────────────────────────────

function CalendarIcon() {
  return (
    <svg className="w-5 h-5 text-primary-500 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M5.75 2a.75.75 0 01.75.75V4h7V2.75a.75.75 0 011.5 0V4h.25A2.75 2.75 0 0118 6.75v8.5A2.75 2.75 0 0115.25 18H4.75A2.75 2.75 0 012 15.25v-8.5A2.75 2.75 0 014.75 4H5V2.75A.75.75 0 015.75 2zm-1 5.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h10.5c.69 0 1.25-.56 1.25-1.25v-6.5c0-.69-.56-1.25-1.25-1.25H4.75z" clipRule="evenodd" />
    </svg>
  )
}

function MapPinIcon({ className = 'w-5 h-5 text-primary-500 shrink-0 mt-0.5' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M9.69 18.933l.003.001C9.89 19.02 10 19 10 19s.11.02.308-.066l.002-.001.006-.003.018-.008a5.741 5.741 0 00.281-.14c.186-.096.446-.24.757-.433.62-.384 1.445-.966 2.274-1.765C15.302 15.027 17 12.49 17 9A7 7 0 103 9c0 3.49 1.698 6.027 3.354 7.584a13.731 13.731 0 002.273 1.765 11.842 11.842 0 00.976.544l.062.029.018.008.006.003zM10 11.25a2.25 2.25 0 100-4.5 2.25 2.25 0 000 4.5z" clipRule="evenodd" />
    </svg>
  )
}

function PeopleIcon() {
  return (
    <svg className="w-5 h-5 text-primary-500 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path d="M7 8a3 3 0 100-6 3 3 0 000 6zM14.5 9a2.5 2.5 0 100-5 2.5 2.5 0 000 5zM1.615 16.428a1.224 1.224 0 01-.569-1.175 6.002 6.002 0 0111.908 0c.058.467-.172.92-.57 1.174A9.953 9.953 0 017 17a9.953 9.953 0 01-5.385-1.572zM14.5 16h-.106c.07-.297.088-.611.048-.933a7.47 7.47 0 00-1.588-3.755 4.502 4.502 0 015.874 2.636.818.818 0 01-.36.98A7.465 7.465 0 0114.5 16z" />
    </svg>
  )
}

function TicketIcon() {
  return (
    <svg className="w-5 h-5 text-primary-500 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path d="M13.833 2.25a.5.5 0 00-.5.5v.614l-.79.455-1.14-.658a.5.5 0 00-.5 0l-.875.505a.5.5 0 00-.25.433v1.31l-.79.456-1.14-.658a.5.5 0 00-.5 0l-.875.505a.5.5 0 00-.25.433V7.25a.5.5 0 00.5.5h.75v7.5a.5.5 0 00.5.5h6.5a.5.5 0 00.5-.5v-7.5h.75a.5.5 0 00.5-.5V4.5a.5.5 0 00-.25-.433l-.875-.505a.5.5 0 00-.5 0l-1.14.658-.79-.455V2.75a.5.5 0 00-.5-.5z" />
    </svg>
  )
}

function ExternalLinkIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M4.25 5.5a.75.75 0 00-.75.75v8.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75v-4a.75.75 0 011.5 0v4A2.25 2.25 0 0112.75 17h-8.5A2.25 2.25 0 012 14.75v-8.5A2.25 2.25 0 014.25 4h5a.75.75 0 010 1.5h-5z" clipRule="evenodd" />
      <path fillRule="evenodd" d="M6.194 12.753a.75.75 0 001.06.053L16.5 4.44v2.81a.75.75 0 001.5 0v-4.5a.75.75 0 00-.75-.75h-4.5a.75.75 0 000 1.5h2.553l-9.056 8.194a.75.75 0 00-.053 1.06z" clipRule="evenodd" />
    </svg>
  )
}

function BackArrowIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
      <path fillRule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clipRule="evenodd" />
    </svg>
  )
}
