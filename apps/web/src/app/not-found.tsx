import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Page Not Found — NovaKidLife',
  robots: { index: false, follow: false },
}

export default function NotFound() {
  return (
    <main className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center">
        <p className="text-6xl font-heading font-extrabold text-primary-200 mb-4">404</p>
        <h1 className="font-heading font-bold text-2xl text-secondary-900 mb-3">
          Page not found
        </h1>
        <p className="text-secondary-500 mb-8 max-w-sm mx-auto">
          This page doesn&apos;t exist or may have moved. Let&apos;s get you back to NoVa family events.
        </p>
        <Link
          href="/events"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors"
        >
          Browse Events
        </Link>
      </div>
    </main>
  )
}
