---
name: seo-schema
description: JSON-LD structured data reference for NovaKidLife — all required schemas per page type, exact blocks, and field conventions. Activates any time a new page type is added or metadata generation is touched.
triggers:
  - JSON-LD
  - structured data
  - schema
  - rich results
  - FAQPage
  - Event schema
  - ItemList
  - LocalBusiness
---

# Skill: SEO Schema — Structured Data Reference

**Activation:** Apply any time a new page type is added or metadata/JSON-LD generation is touched.

> **Note:** FAQPage schema is also a GEO boost — AI systems (Perplexity, ChatGPT, Google AI Overviews) extract FAQ question/answer pairs directly. Keep questions phrased as natural parent queries, not marketing copy.

---

## 1. Event Detail Page — 3 Required Schemas

### Schema 1: Event (enables Google rich results)

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "{title}",
  "description": "{description, first 500 chars}",
  "startDate": "{ISO 8601 with timezone, e.g. 2026-03-21T10:00:00-04:00}",
  "endDate": "{ISO 8601 or omit if null}",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "{location_name}",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "{location_address}",
      "addressLocality": "{city}",
      "addressRegion": "VA",
      "addressCountry": "US"
    }
  },
  "image": ["{og_image_url}", "{image_url}"],
  "organizer": {
    "@type": "Organization",
    "name": "NovaKidLife",
    "url": "https://novakidlife.com"
  },
  "isAccessibleForFree": true,
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "{registration_url or event page url}"
  },
  "url": "https://novakidlife.com/events/{slug}"
}
```

### Schema 2: BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home",   "item": "https://novakidlife.com" },
    { "@type": "ListItem", "position": 2, "name": "Events", "item": "https://novakidlife.com/events" },
    { "@type": "ListItem", "position": 3, "name": "{event title}" }
  ]
}
```

### Schema 3: FAQPage (GEO boost — phrase questions as real parent queries)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is {title} free?",
      "acceptedAnswer": { "@type": "Answer", "text": "Yes, {title} is free to attend." }
    },
    {
      "@type": "Question",
      "name": "Where is {title} held?",
      "acceptedAnswer": { "@type": "Answer", "text": "{title} is held at {location_name} in {city}, Virginia." }
    },
    {
      "@type": "Question",
      "name": "What age is {title} for?",
      "acceptedAnswer": { "@type": "Answer", "text": "{Age range or 'All ages welcome'}" }
    },
    {
      "@type": "Question",
      "name": "How do I register for {title}?",
      "acceptedAnswer": { "@type": "Answer", "text": "{Registration info or 'No registration required.'}" }
    }
  ]
}
```

---

## 2. Homepage — 2 Required Schemas

### Schema 1: WebSite (enables Google sitelinks searchbox)

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "NovaKidLife",
  "url": "https://novakidlife.com",
  "description": "Family events discovery platform for Northern Virginia",
  "potentialAction": {
    "@type": "SearchAction",
    "target": { "@type": "EntryPoint", "urlTemplate": "https://novakidlife.com/events?q={search_term_string}" },
    "query-input": "required name=search_term_string"
  }
}
```

### Schema 2: LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "NovaKidLife",
  "url": "https://novakidlife.com",
  "description": "The most complete family events guide for Northern Virginia.",
  "areaServed": [
    { "@type": "County", "name": "Fairfax County",        "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Loudoun County",        "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Arlington County",      "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "County", "name": "Prince William County", "containedInPlace": { "@type": "State", "name": "Virginia" } }
  ],
  "knowsAbout": ["Family Events", "Kids Activities", "Northern Virginia", "Pokémon TCG Events"]
}
```

---

## 3. Events Listing Page — ItemList Schema

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Family Events in Northern Virginia",
  "description": "Upcoming family events and kids activities in Northern Virginia",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "url": "https://novakidlife.com/events/{slug}" }
  ]
}
```

---

## 4. Implementation Notes

- All three event detail schemas should be rendered as separate `<script type="application/ld+json">` tags — do not combine into one block (Google processes them independently)
- `EventJsonLd.tsx` component already handles all three schemas for event detail pages — check it before adding schema elsewhere
- `extractCity()` in `EventJsonLd.tsx` parses city from address, falls back to "Northern Virginia"
- For local signal extensions (GeoCoordinates, Service Area, zip codes on events), cross-reference `local-seo-schema.md` — that file contains local-specific overlays on top of these base blocks
