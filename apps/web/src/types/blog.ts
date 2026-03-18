import type { Event } from './events'

export type PostType =
  | 'weekend_roundup'
  | 'week_ahead'
  | 'location_specific'
  | 'free_events'
  | 'indoor'
  | 'date_specific'

export type PostArea =
  | 'nova'
  | 'fairfax'
  | 'loudoun'
  | 'arlington'
  | 'alexandria'
  | 'prince_william'
  | 'dc_adjacent'

export interface BlogPost {
  id: string
  slug: string
  title: string
  meta_description: string | null
  content: string            // markdown
  post_type: PostType
  area: PostArea
  date_range_start: string   // ISO date YYYY-MM-DD
  date_range_end: string
  event_count: number
  event_ids: string[]
  hero_image_url: string | null
  published_at: string
}

export interface BlogPostWithEvents extends BlogPost {
  events: EventPreview[]
}

// Lightweight event shape returned with blog post detail
export interface EventPreview {
  id: string
  slug: string
  title: string
  start_at: string
  venue_name: string
  location_text: string | null
  is_free: boolean
  cost_description: string | null
  tags: string[]
  event_type: string
  image_url_sm: string | null
  image_alt: string | null
  image_blurhash: string | null
  image_width: number | null
  image_height: number | null
}

export interface BlogPostsResponse {
  items: BlogPost[]
  total: number
  limit: number
  offset: number
  has_more: boolean
}

export interface BlogPostsParams {
  limit?: number
  offset?: number
  post_type?: PostType
  area?: PostArea
}

// Human-readable labels for display
export const POST_TYPE_LABELS: Record<PostType, string> = {
  weekend_roundup:   'This Weekend',
  week_ahead:        'This Week',
  location_specific: 'By Location',
  free_events:       'Free Events',
  indoor:            'Indoor Activities',
  date_specific:     'Specific Date',
}

export const AREA_LABELS: Record<PostArea, string> = {
  nova:          'Northern Virginia',
  fairfax:       'Fairfax County',
  loudoun:       'Loudoun County',
  arlington:     'Arlington',
  alexandria:    'Alexandria',
  prince_william:'Prince William County',
  dc_adjacent:   'DC Area',
}
