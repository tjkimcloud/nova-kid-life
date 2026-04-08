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

export function EventsClient() {
  const router       = useRouter()
  const pathname     = usePathname()
  const searchParams = useSearchParams()

  // ── Derive filter state directly from URL (source of truth) ──────────────────
  // Using useState caused a bug: in Next.js 15 static export, useSearchParams()
  // returns empty during the hydration pass so useState captured stale initial
  // values. Deriving from searchParams directly means the fetch effect re-runs
  // automatically whenever the URL changes (Link navigation, browser back/forward).
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
  function pushUrl(q: string, f: Filters, p: number, loc?: string) {
    const params = new URLSearchParams()
    if (q)                        params.set('q', q)
    if (f.datePreset)             params.set('date', f.datePreset)
    if (f.category)               params.set('category', f.category)
    if (f.isFree)                 params.set('free', 'true')
    if (loc ?? location)          params.set('location', loc ?? location)
    if (p > 1)                    params.set('page', String(p))
    const qs = params.toString()
    router.replace(`${pathname}${qs ? `?${qs}` : ''}`, { scroll: false })
  }

  // ── Fetch events ──────────────────────────────────────────────────────────────
  const fetchEvents = useCallback(async (q: string, f: Filters, p: number) => {
    if (abortRef.current) abortRef.current.abort()

    if (q.trim()) {
      setSearching(true)
      setLoading(true)
      try {
        const results = await searchEvents(q.trim())
        setAllEvents(results)
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
    // When filtering by location fetch a larger batch — filter client-side
    // since the API has no city-name filter param.
    const hasLocation = !!searchParams.get('location')
    try {
      const resp: EventsResponse = await getEvents({
        section:    'main',
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
  // searchParams is the single source of truth — this fires on Link navigation,
  // browser back/forward, and user filter interactions (which call pushUrl).
  useEffect(() => {
    fetchEvents(query, filters, page)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  // ── Handlers (update URL → triggers re-fetch via searchParams effect) ─────────
  function handleSearch(q: string) {
    pushUrl(q, filters, 1)
  }

  function handleFilters(f: Filters) {
    pushUrl(query, f, 1)
  }

  function handleClearAll() {
    pushUrl('', { datePreset: '', category: '', isFree: false }, 1)
  }

  function handlePage(p: number) {
    pushUrl(query, filters, p)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const hasActiveFilters = query !== '' || filters.datePreset !== '' || filters.category !== '' || filters.isFree

  return (
    <div className="flex flex-col gap-6">
      {/* Search */}
      <SearchBar
        value={query}
        onChange={handleSearch}
        isSearching={searching}
      />

      {/* Filters */}
      <FilterBar
        filters={filters}
        categories={categories}
        totalCount={total}
        onChange={handleFilters}
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
