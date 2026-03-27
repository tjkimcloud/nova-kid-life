export interface Event {
  id: string
  slug: string
  title: string
  description: string
  start_at: string
  end_at: string | null
  location_name: string
  location_address: string | null
  lat: number | null
  lng: number | null
  event_type: EventType
  section: 'main' | 'pokemon'
  brand: string | null
  tags: string[]
  age_min: number | null
  age_max: number | null
  is_free: boolean
  cost_description: string | null
  registration_url: string | null
  source_url: string | null
  source_name: string | null
  image_url: string | null
  image_url_md: string | null
  image_url_sm: string | null
  image_alt: string | null
  image_blurhash: string | null
  image_width: number | null
  image_height: number | null
  og_image_url: string | null
  social_image_url: string | null
  categories?: { name: string; slug: string } | null
}

export type EventType =
  | 'event'
  | 'deal'
  | 'birthday_freebie'
  | 'amusement'
  | 'seasonal'
  | 'pokemon_tcg'
  | 'product_drop'

export interface Category {
  id: string
  name: string
  slug: string
  event_count?: number
}

export interface Location {
  id: string
  name: string
  slug: string
  lat: number
  lng: number
  event_count?: number
}

export interface EventsResponse {
  items: Event[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export interface EventsParams {
  limit?: number
  offset?: number
  section?: string
  category?: string
  location_id?: string
  start_date?: string
  end_date?: string
  tags?: string
  event_type?: string
  is_free?: boolean
}
