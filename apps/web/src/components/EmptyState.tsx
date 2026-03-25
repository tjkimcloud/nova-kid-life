interface EmptyStateProps {
  hasFilters:  boolean
  datePreset?: string
  onClear:     () => void
  onWeekView?: () => void
}

export function EmptyState({ hasFilters, datePreset, onClear, onWeekView }: EmptyStateProps) {
  const isWeekend = datePreset === 'weekend'

  if (isWeekend) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center gap-4">
        <div className="text-5xl" aria-hidden="true">📅</div>
        <h2 className="font-heading font-bold text-xl" style={{ color: 'var(--text)' }}>
          Nothing posted for this weekend yet
        </h2>
        <p className="max-w-sm text-sm leading-relaxed" style={{ color: 'var(--text2)' }}>
          NoVa venues typically post weekend events Thursday–Friday. Check back then — or
          browse what's coming up this week and beyond.
        </p>
        <div className="flex gap-3 mt-2 flex-wrap justify-center">
          {onWeekView && (
            <button
              type="button"
              onClick={onWeekView}
              className="px-5 py-2.5 rounded-xl font-semibold text-sm transition-colors"
              style={{ background: 'var(--orange)', color: '#fff' }}
            >
              Show This Week
            </button>
          )}
          <button
            type="button"
            onClick={onClear}
            className="px-5 py-2.5 rounded-xl font-semibold text-sm border transition-colors"
            style={{ borderColor: 'var(--border)', color: 'var(--text2)' }}
          >
            All upcoming events
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-4">
      <div className="text-5xl" aria-hidden="true">🎉</div>
      <h2 className="font-heading font-bold text-xl" style={{ color: 'var(--text)' }}>
        {hasFilters ? 'No events match your filters' : 'No events yet'}
      </h2>
      <p className="max-w-sm text-sm leading-relaxed" style={{ color: 'var(--text2)' }}>
        {hasFilters
          ? 'Try broadening your search or adjusting the date range.'
          : 'Check back soon — we add new events every day from 50+ Northern Virginia sources.'}
      </p>
      {hasFilters && (
        <button
          type="button"
          onClick={onClear}
          className="mt-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-colors"
          style={{ background: 'var(--orange)', color: '#fff' }}
        >
          Clear all filters
        </button>
      )}
    </div>
  )
}
