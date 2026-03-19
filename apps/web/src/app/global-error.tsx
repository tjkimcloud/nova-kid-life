'use client'

export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', fontFamily: 'sans-serif', textAlign: 'center', padding: '1rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.75rem' }}>Something went wrong</h1>
          <button
            onClick={reset}
            style={{ padding: '0.5rem 1.25rem', borderRadius: '0.5rem', background: '#f59e0b', color: '#fff', fontWeight: 600, border: 'none', cursor: 'pointer' }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  )
}
