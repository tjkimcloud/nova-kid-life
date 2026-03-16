import type { Event } from '@/types/events'

const BASE_URL = 'https://novakidlife.com'

interface Props {
  event: Event
}

function buildEventSchema(event: Event) {
  const startDate = new Date(event.start_at).toISOString()
  const endDate   = event.end_at ? new Date(event.end_at).toISOString() : undefined
  const pageUrl   = `${BASE_URL}/${event.section === 'pokemon' ? 'pokemon/events' : 'events'}/${event.slug}`

  return {
    '@context': 'https://schema.org',
    '@type':    'Event',
    name:        event.title,
    description: event.description.slice(0, 500),
    startDate,
    ...(endDate && { endDate }),
    eventStatus:          'https://schema.org/EventScheduled',
    eventAttendanceMode:  'https://schema.org/OfflineEventAttendanceMode',
    location: {
      '@type': 'Place',
      name:    event.location_name,
      address: event.location_address
        ? {
            '@type':          'PostalAddress',
            streetAddress:    event.location_address,
            addressLocality:  extractCity(event),
            addressRegion:    'VA',
            addressCountry:   'US',
          }
        : undefined,
    },
    image: [event.og_image_url, event.image_url].filter(Boolean),
    organizer: {
      '@type': 'Organization',
      name:    'NovaKidLife',
      url:     BASE_URL,
    },
    isAccessibleForFree: event.is_free,
    offers: {
      '@type':        'Offer',
      price:          event.is_free ? '0' : (event.cost_description ?? ''),
      priceCurrency:  'USD',
      availability:   'https://schema.org/InStock',
      url:            event.registration_url ?? pageUrl,
    },
    url: pageUrl,
  }
}

function buildBreadcrumbSchema(event: Event) {
  const isPoemon  = event.section === 'pokemon'
  const listUrl   = `${BASE_URL}/${isPoemon ? 'pokemon/events' : 'events'}`
  const listLabel = isPoemon ? 'Pokémon Events' : 'Events'

  return {
    '@context': 'https://schema.org',
    '@type':    'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home',       item: BASE_URL },
      { '@type': 'ListItem', position: 2, name: listLabel,    item: listUrl },
      { '@type': 'ListItem', position: 3, name: event.title },
    ],
  }
}

function buildFaqSchema(event: Event) {
  const ageAnswer =
    event.age_min != null && event.age_max != null
      ? `${event.title} is for children ages ${event.age_min}–${event.age_max}.`
      : event.age_min != null
      ? `${event.title} is for children ages ${event.age_min} and up.`
      : 'All ages are welcome.'

  const regAnswer =
    event.registration_url
      ? `Register online at ${event.registration_url}.`
      : 'No registration required — just show up.'

  return {
    '@context': 'https://schema.org',
    '@type':    'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name:    `Is ${event.title} free?`,
        acceptedAnswer: {
          '@type': 'Answer',
          text:    event.is_free
            ? `Yes, ${event.title} is free to attend.`
            : `${event.title} costs ${event.cost_description ?? 'an admission fee'}.`,
        },
      },
      {
        '@type': 'Question',
        name:    `Where is ${event.title} held?`,
        acceptedAnswer: {
          '@type': 'Answer',
          text:    `${event.title} is held at ${event.location_name} in ${extractCity(event)}, Virginia.`,
        },
      },
      {
        '@type': 'Question',
        name:    `What age is ${event.title} for?`,
        acceptedAnswer: { '@type': 'Answer', text: ageAnswer },
      },
      {
        '@type': 'Question',
        name:    `How do I register for ${event.title}?`,
        acceptedAnswer: { '@type': 'Answer', text: regAnswer },
      },
    ],
  }
}

/** Extract city from address string or fall back to generic label. */
export function extractCity(event: Event): string {
  if (event.location_address) {
    const m = event.location_address.match(/,\s*([A-Za-z ]+),\s*VA/i)
    if (m) return m[1].trim()
  }
  return 'Northern Virginia'
}

export function EventJsonLd({ event }: Props) {
  const schemas = [
    buildEventSchema(event),
    buildBreadcrumbSchema(event),
    buildFaqSchema(event),
  ]

  return (
    <>
      {schemas.map((schema, i) => (
        <script
          key={i}
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
        />
      ))}
    </>
  )
}
