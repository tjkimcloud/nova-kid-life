import type {
  Event,
  EventsParams,
  EventsResponse,
  Category,
  Location,
} from '@/types/events'
import type {
  BlogPost,
  BlogPostWithEvents,
  BlogPostsResponse,
  BlogPostsParams,
} from '@/types/blog'

const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? '').replace(/\/$/, '')

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, {
    ...options,
    signal: options?.signal ?? AbortSignal.timeout(8000),
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${path}`)
  }
  return res.json() as Promise<T>
}

function buildQuery(params: Record<string, string | number | boolean | undefined>): string {
  const qs = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== '' && v !== null)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join('&')
  return qs ? `?${qs}` : ''
}

// ── Events ─────────────────────────────────────────────────────────────────────

export async function getEvents(params: EventsParams = {}): Promise<EventsResponse> {
  return apiFetch<EventsResponse>(`/events${buildQuery(params as Record<string, string | number | boolean | undefined>)}`)
}

export async function getEvent(slug: string): Promise<Event> {
  return apiFetch<Event>(`/events/${encodeURIComponent(slug)}`)
}

export async function getFeaturedEvents(section = 'main', limit = 6): Promise<Event[]> {
  const data = await apiFetch<{ items: Event[] }>(`/events/featured${buildQuery({ section, limit })}`)
  return data.items
}

export async function getUpcomingEvents(section = 'main', limit = 10): Promise<Event[]> {
  const data = await apiFetch<{ items: Event[] }>(`/events/upcoming${buildQuery({ section, limit })}`)
  return data.items
}

export async function searchEvents(query: string, section = 'main', limit = 10): Promise<Event[]> {
  const data = await apiFetch<{ items: Event[] }>('/events/search', {
    method: 'POST',
    body: JSON.stringify({ query, section, limit }),
  })
  return data.items
}

// ── Reference data ─────────────────────────────────────────────────────────────

export async function getCategories(): Promise<Category[]> {
  const data = await apiFetch<{ categories: Category[] }>('/categories')
  return data.categories
}

export async function getLocations(): Promise<Location[]> {
  const data = await apiFetch<{ locations: Location[] }>('/locations')
  return data.locations
}

// ── Pokémon ────────────────────────────────────────────────────────────────────

export async function getPokemonEvents(params: EventsParams = {}): Promise<EventsResponse> {
  return apiFetch<EventsResponse>(`/pokemon/events${buildQuery(params as Record<string, string | number | boolean | undefined>)}`)
}

export async function getPokemonDrops(params: EventsParams = {}): Promise<EventsResponse> {
  return apiFetch<EventsResponse>(`/pokemon/drops${buildQuery(params as Record<string, string | number | boolean | undefined>)}`)
}

// ── Blog ────────────────────────────────────────────────────────────────────────

export async function getBlogPosts(params: BlogPostsParams = {}): Promise<BlogPostsResponse> {
  return apiFetch<BlogPostsResponse>(`/blog${buildQuery(params as Record<string, string | number | boolean | undefined>)}`)
}

export async function getBlogPost(slug: string): Promise<BlogPostWithEvents> {
  return apiFetch<BlogPostWithEvents>(`/blog/${encodeURIComponent(slug)}`)
}

export async function getLatestWeekendRoundup(): Promise<BlogPost | null> {
  const data = await getBlogPosts({ post_type: 'weekend_roundup', area: 'nova', limit: 1 })
  return data.items[0] ?? null
}
