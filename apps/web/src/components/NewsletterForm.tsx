'use client'

import { useState } from 'react'

export function NewsletterForm() {
  const [email,   setEmail]   = useState('')
  const [status,  setStatus]  = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('loading')
    try {
      const API = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.novakidlife.com'
      const res = await fetch(`${API}/newsletter/subscribe`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email }),
      })
      if (!res.ok) throw new Error('Failed')
      setStatus('success')
      setMessage("You're in! Check your inbox for the first roundup.")
      setEmail('')
      window.gtag?.('event', 'newsletter_signup', { method: 'inline_form' })
    } catch {
      setStatus('error')
      setMessage('Something went wrong — please try again.')
    }
  }

  if (status === 'success') {
    return (
      <p className="font-body font-semibold text-sm py-3" style={{ color: 'var(--orange)' }}>
        {message}
      </p>
    )
  }

  return (
    <form onSubmit={handleSubmit} aria-label="Newsletter signup">
      {/* Pill-style fused input + button */}
      <div
        className="flex items-center overflow-hidden w-full max-w-md mx-auto"
        style={{
          background:    '#fff',
          borderRadius:  '999px',
          boxShadow:     'var(--shadow)',
          border:        '1.5px solid var(--border)',
        }}
      >
        <label htmlFor="newsletter-email" className="sr-only">Email address</label>
        <input
          id="newsletter-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          disabled={status === 'loading'}
          className="flex-1 min-w-0 px-5 py-3.5 text-sm font-body bg-transparent outline-none placeholder:text-secondary-400 disabled:opacity-60"
          style={{ color: 'var(--text)' }}
        />
        <button
          type="submit"
          disabled={status === 'loading'}
          className="shrink-0 mx-1.5 my-1.5 px-5 py-2.5 text-sm font-body font-semibold text-white rounded-full transition-opacity hover:opacity-90 disabled:opacity-60"
          style={{ background: 'var(--orange)' }}
        >
          {status === 'loading' ? 'Subscribing…' : 'Subscribe'}
        </button>
      </div>

      {status === 'error' && (
        <p className="font-body text-xs mt-2 text-center text-red-500">{message}</p>
      )}

      {/* Benefit chips */}
      <div className="flex flex-wrap justify-center gap-2 mt-4">
        {['Free weekly guide', 'Best local events', 'No spam, ever'].map((b) => (
          <span
            key={b}
            className="font-body text-[11px] font-medium px-3 py-1 rounded-full border"
            style={{ color: 'var(--text2)', borderColor: 'var(--border)', background: '#fff' }}
          >
            {b}
          </span>
        ))}
      </div>
    </form>
  )
}
