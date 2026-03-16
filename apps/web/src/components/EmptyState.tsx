interface EmptyStateProps {
  hasFilters: boolean
  onClear:    () => void
}

export function EmptyState({ hasFilters, onClear }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-4">
      <div className="text-5xl" aria-hidden="true">🎉</div>
      <h2 className="font-heading font-bold text-xl text-secondary-800">
        {hasFilters ? 'No events match your filters' : 'No events yet'}
      </h2>
      <p className="text-secondary-500 max-w-sm text-sm leading-relaxed">
        {hasFilters
          ? 'Try broadening your search or adjusting the date range.'
          : 'Check back soon — we add new events every day from 50+ Northern Virginia sources.'}
      </p>
      {hasFilters && (
        <button
          type="button"
          onClick={onClear}
          className="mt-2 px-5 py-2.5 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors"
        >
          Clear all filters
        </button>
      )}
    </div>
  )
}
