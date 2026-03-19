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
      setMessage('You\'re in! Check your inbox for the first roundup.')
      setEmail('')
    } catch {
      setStatus('error')
      setMessage('Something went wrong — please try again.')
    }
  }

  if (status === 'success') {
    return (
      <p className="text-primary-400 font-semibold text-sm py-3">
        {message}
      </p>
    )
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col sm:flex-row gap-3"
      aria-label="Newsletter signup"
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
        className="flex-1 px-4 py-3 rounded-xl text-sm border border-secondary-600 bg-secondary-700 text-white placeholder-secondary-400 focus:outline-none focus:border-primary-400 disabled:opacity-60"
      />
      <button
        type="submit"
        disabled={status === 'loading'}
        className="px-6 py-3 rounded-xl bg-primary-500 text-white font-semibold text-sm hover:bg-primary-600 transition-colors shrink-0 disabled:opacity-60"
      >
        {status === 'loading' ? 'Subscribing…' : 'Subscribe'}
      </button>
      {status === 'error' && (
        <p className="text-red-400 text-xs mt-1 w-full">{message}</p>
      )}
    </form>
  )
}
