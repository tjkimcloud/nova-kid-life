---
name: local-seo-schema
description: Local-signal schema extensions for NovaKidLife — GeoCoordinates, Service Area Business with GeoCircle, Event with Place including zip codes, ItemList for location pages with areaServed, and Pokémon TCG local SEO schema. Contains only the local-signal overlays on top of the base schemas in seo-schema.md. Activates any session adding location pages, event pages, or anything in the Pokémon section.
triggers:
  - GeoCoordinates
  - service area schema
  - areaServed
  - PostalAddress
  - GeoCircle
  - location page schema
  - Pokémon schema
  - ItemList location
---

# Skill: Local SEO — Schema Extensions

**Activation:** Any session adding location pages, event pages, or anything in the Pokémon section.

> **Note:** This file contains ONLY the local-signal extensions. Cross-reference `seo-schema.md` for the base Event, FAQPage, BreadcrumbList, and ItemList blocks that these extend.

---

## 1. GeoCoordinates (add to location pages)

```json
{
  "@type": "LocalBusiness",
  "name": "NovaKidLife",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude":  38.8816,
    "longitude": -77.1073
  }
}
```

Use the geographic center of the NoVa service area (approximate center between Fairfax and Loudoun counties).

---

## 2. Service Area Business with GeoCircle

```json
{
  "@type": "LocalBusiness",
  "name": "NovaKidLife",
  "areaServed": [
    { "@type": "City", "name": "Reston",    "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Fairfax",   "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Chantilly", "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Herndon",   "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "McLean",    "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Vienna",    "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Leesburg",  "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Ashburn",   "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Sterling",  "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Manassas",  "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Woodbridge","containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Alexandria","containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Arlington", "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Burke",     "containedInPlace": { "@type": "State", "name": "Virginia" } },
    { "@type": "City", "name": "Springfield","containedInPlace": { "@type": "State", "name": "Virginia" } }
  ],
  "serviceArea": {
    "@type": "GeoCircle",
    "geoMidpoint": {
      "@type": "GeoCoordinates",
      "latitude":  38.8816,
      "longitude": -77.1073
    },
    "geoRadius": "80000"
  }
}
```

Note: `geoRadius` is in meters. 80000m ≈ 50 miles — covers all of NoVa service area.

---

## 3. Event with Place — Full Local Signal

Use this overlay on every event page instead of the basic location block. The zip code (`postalCode`) is a local ranking signal — include it whenever available.

```json
{
  "@type": "Event",
  "location": {
    "@type": "Place",
    "name": "Fairfax County Library — Chantilly Branch",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "4100 Stringfellow Rd",
      "addressLocality": "Chantilly",
      "addressRegion": "VA",
      "postalCode": "20151",
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude":  38.8903,
      "longitude": -77.4352
    }
  }
}
```

Rules:
- Include `geo` + full `PostalAddress` on every event — zip code is a local ranking signal
- `postalCode` comes from the event's `address` field in the DB — parse it or store separately
- If no `postalCode` available, omit the field rather than leaving it blank

---

## 4. ItemList for Location Pages

Use on `/locations/[city-slug]` pages to signal regional authority:

```json
{
  "@type": "ItemList",
  "name": "Family Events in Reston, VA",
  "description": "Upcoming family events and kids activities in Reston, Virginia",
  "areaServed": {
    "@type": "City",
    "name": "Reston",
    "containedInPlace": { "@type": "State", "name": "Virginia" }
  },
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "url": "https://novakidlife.com/events/{slug}" },
    { "@type": "ListItem", "position": 2, "url": "https://novakidlife.com/events/{slug}" }
  ]
}
```

---

## 5. Pokémon TCG Local SEO

### Target Queries

- `pokemon tcg league [city] va` — near-zero competition
- `pokemon prerelease northern virginia`
- `where to buy pokemon cards [city] va`
- `nerd rage gaming pokemon`
- `battlegrounds gaming pokemon league`
- `pokemon tournament fairfax county`

### LGS Page Schema

Each Local Game Store event page should use the Event schema from `seo-schema.md` with this enhanced location block:

```json
{
  "@type": "Event",
  "name": "Pokemon TCG League Night — Nerd Rage Gaming",
  "location": {
    "@type": "GameStore",
    "name": "Nerd Rage Gaming",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "{address}",
      "addressLocality": "Manassas",
      "addressRegion": "VA",
      "postalCode": "{zip}",
      "addressCountry": "US"
    }
  }
}
```

Use `"@type": "GameStore"` (a subtype of `LocalBusiness`) for LGS venues — more specific type = stronger local signal.

### Retailer Matrix SEO

The `/pokemon` retailer matrix page is a featured snippet opportunity for "where to buy pokemon cards nova". Optimize with:
- H2 per retailer category (Big Box, LGS, Online)
- H3 per store with full address and "near [landmark]" phrasing
- Link to official Play! Pokémon event locator (legitimate external link)
- FAQPage schema with Pokemon-specific parent queries

### Pokémon Community Link Targets

- Limitless TCG (limitlessTCG.com) — tournament results, NoVa player community
- Local NoVa Facebook groups: "NoVa Pokémon TCG", "DC/MD/VA Pokémon"
- Play! Pokémon official locator page — get stores to list NovaKidLife as a resource
