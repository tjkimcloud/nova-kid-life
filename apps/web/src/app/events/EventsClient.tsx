'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { useRouter, useSearchParams, usePathname } from 'next/navigation'

import { getEvents, getCategories, searchEvents } from '@/lib/api'
import type { Category, Event, EventsResponse } from '@/types/events'

import { EventGrid }          from '@/components/EventGrid'
import { EventGridSkeleton }  from '@/components/EventCardSkeleton'
import { SearchBar }          from '@/components/SearchBar'
import { FilterBar, Filters, getDateRange } from '@/components/FilterBar'
import { Pagination }         from '@/components/Pagination'
import { EmptyState }         from '@/components/EmptyState'

const PAGE_SIZE = 12

// Event types that belong in each tab
const TAB_EVENT_TYPES = {
  events: 'event,amusement,seasonal',
  deals:  'deal,birthday_freebie,product_drop',
} as const

type Tab = keyof typeof TAB_EVENT_TYPES

const TABS: { key: Tab; label: string; description: string }[] = [
  {
    key:         'events',
    label:       'Local Events',
    description: 'Storytime, STEM, outdoor adventures, classes, and community events',
  },
  {
    key:         'deals',
    label:       'Deals & Freebies',
    description: 'Restaurant promos, birthday freebies, and family discounts',
  },
]

export function EventsClient() {
  const router       = useRouter()
  const pathname     = usePathname()
  const searchParams = useSearchParams()

  // ── Derive all state directly from URL (source of truth) ─────────────────────
  const rawTab   = searchParams.get('tab')
  const tab: Tab = rawTab !== null && rawTab in TAB_EVENT_TYPES ? (rawTab as Tab) : 'events'

  const filters: Filters = {
    datePreset: (searchParams.get('date') as Filters['datePreset']) || '',
    category:   searchParams.get('category') || '',
    isFree:     searchParams.get('free') === 'true',
  }
  const query    = searchParams.get('q') || ''
  const location = searchParams.get('location') || ''
  const page     = Number(searchParams.get('page') || 1)

  // ── UI-only state ─────────────────────────────────────────────────────────────
  const [loading,    setLoading]    = useState(true)
  const [searching,  setSearching]  = useState(false)
  const [allEvents,  setAllEvents]  = useState<Event[]>([])
  const [total,      setTotal]      = useState(0)
  const [categories, setCategories] = useState<Category[]>([])

  // Apply location filter client-side (API has no city-name filter param)
  const events = location
    ? allEvents.filter(ev => {
        const haystack = `${ev.location_name ?? ''} ${ev.location_address ?? ''}`.toLowerCase()
        return haystack.includes(location.toLowerCase())
      })
    : allEvents

  const abortRef = useRef<AbortController | null>(null)

  const totalPages = Math.ceil(total / PAGE_SIZE)

  // ── Sync URL ──────────────────────────────────────────────────────────────────
  function pushUrl(q: string, f: Filters, p: number, loc?: string, nextTab?: Tab) {
    const params = new URLSearchParams()
    const activeTab = nextTab ?? tab
    if (activeTab !== 'events') params.set('tab', activeTab)
    if (q)                      params.set('q', q)
    if (f.datePreset)           params.set('date', f.datePreset)
    if (f.category)             params.set('category', f.category)
    if (f.isFree)               params.set('free', 'true')
    if (loc ?? location)        params.set('location', loc ?? location)
    if (p > 1)                  params.set('page', String(p))
    const qs = params.toString()
    router.replace(`${pathname}${qs ? `?${qs}` : ''}`, { scroll: false })
  }

  function handleTabChange(newTab: Tab) {
    // Reset all filters when switching tabs
    const params = new URLSearchParams()
    if (newTab !== 'events') params.set('tab', newTab)
    const qs = params.toString()
    router.replace(`${pathname}${qs ? `?${qs}` : ''}`, { scroll: false })
  }

  // ── Fetch events ──────────────────────────────────────────────────────────────
  const fetchEvents = useCallback(async (q: string, f: Filters, p: number, activeTab: Tab) => {
    if (abortRef.current) abortRef.current.abort()

    if (q.trim()) {
      setSearching(true)
      setLoading(true)
      try {
        const results = await searchEvents(q.trim())
        // Filter search results to the active tab's event types
        const typeSet = new Set(TAB_EVENT_TYPES[activeTab].split(','))
        setAllEvents(results.filter(e => typeSet.has(e.event_type)))
        setTotal(results.length)
      } catch {
        setAllEvents([])
        setTotal(0)
      } finally {
        setLoading(false)
        setSearching(false)
      }
      return
    }

    setLoading(true)
    const dateRange = getDateRange(f.datePreset)
    const hasLocation = !!searchParams.get('location')
    try {
      const resp: EventsResponse = await getEvents({
        section:    'main',
        event_type: TAB_EVENT_TYPES[activeTab],
        category:   f.category  || undefined,
        is_free:    f.isFree    || undefined,
        start_date: dateRange.start_date,
        end_date:   dateRange.end_date,
        limit:      hasLocation ? 200 : PAGE_SIZE,
        offset:     hasLocation ? 0 : (p - 1) * PAGE_SIZE,
      })
      setAllEvents(resp.items)
      setTotal(resp.total)
    } catch {
      setAllEvents([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Load categories once ──────────────────────────────────────────────────────
  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]))
  }, [])

  // ── Re-fetch whenever URL changes ─────────────────────────────────────────────
  useEffect(() => {
    fetchEvents(query, filters, page, tab)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  // ── Handlers ──────────────────────────────────────────────────────────────────
  function handleSearch(q: string)   { pushUrl(q, filters, 1) }
  function handleFilters(f: Filters) { pushUrl(query, f, 1) }
  function handleClearAll()          { pushUrl('', { datePreset: '', category: '', isFree: false }, 1) }
  function handlePage(p: number) {
    pushUrl(query, filters, p)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const hasActiveFilters = query !== '' || filters.datePreset !== '' || filters.category !== '' || filters.isFree
  const activeTabMeta    = TABS.find(t => t.key === tab)!

  return (
    <div className="flex flex-col gap-6">

      {/* ── Tab bar ──────────────────────────────────────────────────── */}
      <div
        className="flex rounded-xl p-1 gap-1"
        style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}
        role="tablist"
        aria-label="Event categories"
      >
        {TABS.map(({ key, label }) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={tab === key}
            onClick={() => handleTabChange(key)}
            className="flex-1 px-4 py-2.5 rounded-lg font-body font-semibold text-sm transition-all"
            style={tab === key ? {
              background:  'var(--white)',
              color:       'var(--text)',
              boxShadow:   'var(--shadow-sm)',
            } : {
              color:       'var(--text2)',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab description */}
      <p className="text-[13px] -mt-2" style={{ color: 'var(--text3)' }}>
        {activeTabMeta.description}
      </p>

      {/* Search */}
      <SearchBar
        value={query}
        onChange={handleSearch}
        isSearching={searching}
      />

      {/* Filters — hide date presets on Deals tab since deals are ongoing */}
      <FilterBar
        filters={filters}
        categories={categories}
        totalCount={total}
        onChange={handleFilters}
        hideDatePresets={tab === 'deals'}
      />

      {/* Results */}
      {loading ? (
        <EventGridSkeleton count={PAGE_SIZE} />
      ) : events.length === 0 ? (
        <EmptyState
          hasFilters={hasActiveFilters}
          datePreset={filters.datePreset}
          onClear={handleClearAll}
          onWeekView={() => handleFilters({ ...filters, datePreset: 'week' })}
        />
      ) : (
        <>
          <EventGrid events={events} />
          {filters.datePreset === 'weekend' && events.length < 4 && (
            <p className="text-center text-xs pt-2 pb-4" style={{ color: 'var(--text2)' }}>
              Venues typically post weekend events closer to Thursday–Friday.{' '}
              <button
                type="button"
                className="underline hover:no-underline"
                style={{ color: 'var(--orange)' }}
                onClick={() => handleFilters({ ...filters, datePreset: 'week' })}
              >
                Browse this week
              </button>{' '}for more.
            </p>
          )}
          <Pagination
            page={page}
            totalPages={totalPages}
            onChange={handlePage}
          />
        </>
      )}
    </div>
  )
}
