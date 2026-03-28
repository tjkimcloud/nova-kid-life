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
  const router     = useRouter()
  const pathname   = usePathname()
  const searchParams = useSearchParams()

  // ── Read initial state from URL ──────────────────────────────────────────────
  const initialFilters: Filters = {
    datePreset: (searchParams.get('date') as Filters['datePreset']) || '',
    category:   searchParams.get('category') || '',
    isFree:     searchParams.get('free') === 'true',
  }
  const initialQuery  = searchParams.get('q') || ''
  const initialPage   = Number(searchParams.get('page') || 1)

  // ── State ────────────────────────────────────────────────────────────────────
  const [filters,    setFilters]    = useState<Filters>(initialFilters)
  const [query,      setQuery]      = useState(initialQuery)
  const [page,       setPage]       = useState(initialPage)
  const [loading,    setLoading]    = useState(true)
  const [searching,  setSearching]  = useState(false)
  const [events,     setEvents]     = useState<Event[]>([])
  const [total,      setTotal]      = useState(0)
  const [categories, setCategories] = useState<Category[]>([])

  const abortRef    = useRef<AbortController | null>(null)
  const hasMounted  = useRef(false)

  const totalPages = Math.ceil(total / PAGE_SIZE)

  // ── Sync state → URL ─────────────────────────────────────────────────────────
  function pushUrl(q: string, f: Filters, p: number) {
    const params = new URLSearchParams()
    if (q)             params.set('q', q)
    if (f.datePreset)  params.set('date', f.datePreset)
    if (f.category)    params.set('category', f.category)
    if (f.isFree)      params.set('free', 'true')
    if (p > 1)         params.set('page', String(p))
    const qs = params.toString()
    router.replace(`${pathname}${qs ? `?${qs}` : ''}`, { scroll: false })
  }

  // ── Fetch events ──────────────────────────────────────────────────────────────
  const fetchEvents = useCallback(async (q: string, f: Filters, p: number) => {
    if (abortRef.current) abortRef.current.abort()

    if (q.trim()) {
      // Semantic search path
      setSearching(true)
      setLoading(true)
      try {
        const results = await searchEvents(q.trim())
        setEvents(results)
        setTotal(results.length)
        setPage(1)
      } catch {
        setEvents([])
        setTotal(0)
      } finally {
        setLoading(false)
        setSearching(false)
      }
      return
    }

    // Filter path
    setLoading(true)
    const dateRange = getDateRange(f.datePreset)
    try {
      const resp: EventsResponse = await getEvents({
        section:    'main',
        category:   f.category  || undefined,
        is_free:    f.isFree    || undefined,
        start_date: dateRange.start_date,
        end_date:   dateRange.end_date,
        limit:      PAGE_SIZE,
        offset:     (p - 1) * PAGE_SIZE,
      })
      setEvents(resp.items)
      setTotal(resp.total)
    } catch {
      setEvents([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  // ── Load categories once ──────────────────────────────────────────────────────
  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]))
  }, [])

  // ── Re-fetch whenever query/filters/page change ───────────────────────────────
  useEffect(() => {
    // On initial mount the URL is already correct (navigated here via Link or direct URL).
    // Calling router.replace on mount in Next.js 15 triggers a useSearchParams re-render
    // that can abort the in-flight fetch before events arrive.  Skip pushUrl on mount.
    if (hasMounted.current) {
      pushUrl(query, filters, page)
    } else {
      hasMounted.current = true
    }
    fetchEvents(query, filters, page)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, filters, page])

  // ── Handlers ─────────────────────────────────────────────────────────────────
  function handleSearch(q: string) {
    setQuery(q)
    setPage(1)
  }

  function handleFilters(f: Filters) {
    setFilters(f)
    setPage(1)
  }

  function handleClearAll() {
    setQuery('')
    setFilters({ datePreset: '', category: '', isFree: false })
    setPage(1)
  }

  function handlePage(p: number) {
    setPage(p)
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
