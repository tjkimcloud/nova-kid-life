'use client'

import type { Category } from '@/types/events'

export interface Filters {
  datePreset: '' | 'today' | 'weekend' | 'week' | 'month'
  category:   string
  isFree:     boolean
}

interface FilterBarProps {
  filters:    Filters
  categories: Category[]
  totalCount: number
  onChange:   (filters: Filters) => void
}

const DATE_PRESETS: { key: Filters['datePreset']; label: string }[] = [
  { key: 'today',   label: 'Today'        },
  { key: 'weekend', label: 'This Weekend' },
  { key: 'week',    label: 'This Week'    },
  { key: 'month',   label: 'This Month'   },
]

export function getDateRange(preset: Filters['datePreset']): { start_date?: string; end_date?: string } {
  if (!preset) return {}

  const now   = new Date()
  const today = now.toISOString().split('T')[0]

  if (preset === 'today') {
    return { start_date: today, end_date: today }
  }

  if (preset === 'weekend') {
    const day   = now.getDay()           // 0=Sun, 6=Sat
    const toSat = (6 - day + 7) % 7 || 7
    const sat   = new Date(now); sat.setDate(now.getDate() + toSat)
    const sun   = new Date(sat); sun.setDate(sat.getDate() + 1)
    return {
      start_date: sat.toISOString().split('T')[0],
      end_date:   sun.toISOString().split('T')[0] + 'T23:59:59',
    }
  }

  if (preset === 'week') {
    const end = new Date(now); end.setDate(now.getDate() + 7)
    return { start_date: today, end_date: end.toISOString().split('T')[0] + 'T23:59:59' }
  }

  if (preset === 'month') {
    const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    return { start_date: today, end_date: end.toISOString().split('T')[0] + 'T23:59:59' }
  }

  return {}
}

export function FilterBar({ filters, categories, totalCount, onChange }: FilterBarProps) {
  const hasActiveFilters = filters.datePreset !== '' || filters.category !== '' || filters.isFree

  function setPreset(preset: Filters['datePreset']) {
    onChange({ ...filters, datePreset: filters.datePreset === preset ? '' : preset })
  }

  function setCategory(category: string) {
    onChange({ ...filters, category })
  }

  function toggleFree() {
    onChange({ ...filters, isFree: !filters.isFree })
  }

  function clearAll() {
    onChange({ datePreset: '', category: '', isFree: false })
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        {/* Date presets */}
        {DATE_PRESETS.map(({ key, label }) => (
          <button
            key={key}
            type="button"
            onClick={() => setPreset(key)}
            aria-pressed={filters.datePreset === key}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              filters.datePreset === key
                ? 'bg-primary-500 text-white border-primary-500'
                : 'bg-white text-secondary-700 border-secondary-200 hover:border-primary-300 hover:text-primary-700'
            }`}
          >
            {label}
          </button>
        ))}

        {/* Category dropdown */}
        {categories.length > 0 && (
          <select
            value={filters.category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="Filter by category"
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors appearance-none bg-white cursor-pointer ${
              filters.category
                ? 'bg-primary-500 text-white border-primary-500'
                : 'text-secondary-700 border-secondary-200 hover:border-primary-300'
            }`}
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.slug}>
                {cat.name}
                {cat.event_count !== undefined ? ` (${cat.event_count})` : ''}
              </option>
            ))}
          </select>
        )}

        {/* Free toggle */}
        <button
          type="button"
          onClick={toggleFree}
          aria-pressed={filters.isFree}
          className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            filters.isFree
              ? 'bg-secondary-500 text-white border-secondary-500'
              : 'bg-white text-secondary-700 border-secondary-200 hover:border-secondary-400'
          }`}
        >
          🆓 Free only
        </button>

        {/* Clear filters */}
        {hasActiveFilters && (
          <button
            type="button"
            onClick={clearAll}
            className="px-3 py-1.5 rounded-full text-sm font-medium text-secondary-500 hover:text-secondary-700 underline underline-offset-2 transition-colors"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Result count */}
      <p className="text-sm text-secondary-500">
        {totalCount > 0
          ? `${totalCount.toLocaleString()} event${totalCount === 1 ? '' : 's'} found`
          : null}
      </p>
    </div>
  )
}
