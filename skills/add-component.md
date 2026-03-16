# Skill: Add React Component

**Purpose:** Scaffold a new reusable UI component following project conventions.

## Component Checklist
- [ ] Named export (not default export)
- [ ] TypeScript props interface
- [ ] Tailwind classes only (no inline styles except CSS vars)
- [ ] `'use client'` only if using state, effects, or browser APIs
- [ ] Placed in `apps/web/src/components/`

## Template

```tsx
// apps/web/src/components/EventCard.tsx

interface EventCardProps {
  title: string
  date: string
  location: string
  imageUrl?: string
}

export function EventCard({ title, date, location, imageUrl }: EventCardProps) {
  return (
    <article className="bg-white rounded-2xl overflow-hidden shadow-sm border border-stone-100 hover:shadow-md transition-shadow">
      {imageUrl && (
        <div className="aspect-video relative overflow-hidden">
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      <div className="p-4">
        <h3 className="font-heading font-bold text-lg text-stone-800 mb-1">
          {title}
        </h3>
        <p className="font-body text-sm text-primary-600 font-medium mb-1">
          {date}
        </p>
        <p className="font-body text-sm text-stone-500">
          {location}
        </p>
      </div>
    </article>
  )
}
```

## Steps

1. Create the file at `apps/web/src/components/<ComponentName>.tsx`
2. Add a named export with props interface
3. Use `font-heading` for headings, `font-body` for body text
4. Use `primary-*` and `secondary-*` Tailwind tokens for brand colors
5. Import and use in the target page

## Client Components

Only add `'use client'` when the component:
- Uses `useState`, `useEffect`, `useReducer`
- Uses browser APIs (`window`, `document`, `localStorage`)
- Handles DOM events
- Uses third-party client-only libraries

## Server Components (default)

Server components can:
- Fetch data directly (async functions)
- Access backend resources
- Reduce client JS bundle

## Index Export (optional)

If building a component library in a directory:
```tsx
// apps/web/src/components/index.ts
export { EventCard } from './EventCard'
export { EventGrid } from './EventGrid'
```
