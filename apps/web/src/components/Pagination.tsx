'use client'

interface PaginationProps {
  page:       number
  totalPages: number
  onChange:   (page: number) => void
}

export function Pagination({ page, totalPages, onChange }: PaginationProps) {
  if (totalPages <= 1) return null

  // Build page number list with ellipsis: 1 ... 4 5 6 ... 12
  function getPages(): (number | '…')[] {
    if (totalPages <= 7) return Array.from({ length: totalPages }, (_, i) => i + 1)

    const pages: (number | '…')[] = [1]
    if (page > 3) pages.push('…')

    const start = Math.max(2, page - 1)
    const end   = Math.min(totalPages - 1, page + 1)
    for (let i = start; i <= end; i++) pages.push(i)

    if (page < totalPages - 2) pages.push('…')
    pages.push(totalPages)

    return pages
  }

  const pages = getPages()

  return (
    <nav aria-label="Pagination" className="flex items-center justify-center gap-1">
      {/* Previous */}
      <button
        type="button"
        onClick={() => onChange(page - 1)}
        disabled={page === 1}
        aria-label="Previous page"
        className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium text-secondary-600 hover:text-primary-700 hover:bg-primary-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
        </svg>
        Prev
      </button>

      {/* Page numbers */}
      {pages.map((p, i) =>
        p === '…' ? (
          <span key={`ellipsis-${i}`} className="px-2 py-2 text-secondary-400 text-sm select-none">
            …
          </span>
        ) : (
          <button
            key={p}
            type="button"
            onClick={() => onChange(p)}
            aria-label={`Page ${p}`}
            aria-current={p === page ? 'page' : undefined}
            className={`min-w-[2.25rem] px-2 py-2 rounded-lg text-sm font-medium transition-colors ${
              p === page
                ? 'bg-primary-500 text-white'
                : 'text-secondary-700 hover:bg-primary-50 hover:text-primary-700'
            }`}
          >
            {p}
          </button>
        )
      )}

      {/* Next */}
      <button
        type="button"
        onClick={() => onChange(page + 1)}
        disabled={page === totalPages}
        aria-label="Next page"
        className="flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium text-secondary-600 hover:text-primary-700 hover:bg-primary-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        Next
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
        </svg>
      </button>
    </nav>
  )
}
