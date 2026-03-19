'use client'

import Link from 'next/link'

export default function Error({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <main className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center">
        <p className="text-5xl mb-4">😕</p>
        <h2 className="font-heading font-bold text-2xl text-secondary-900 mb-3">
          Something went wrong
        </h2>
        <p className="text-secondary-500 mb-6 max-w-sm mx-auto text-sm">
          An unexpected error occurred. Try refreshing the page or browse events below.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors"
          >
            Try again
          </button>
          <Link
            href="/events"
            className="px-6 py-3 rounded-xl border border-secondary-200 text-secondary-700 font-semibold text-sm hover:bg-secondary-50 transition-colors"
          >
            Browse Events
          </Link>
        </div>
      </div>
    </main>
  )
}
