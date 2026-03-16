'use client'

import { useEffect, useRef, useState } from 'react'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  isSearching?: boolean
}

export function SearchBar({
  value,
  onChange,
  placeholder = 'Search events — "science for 5 year olds", "free outdoor activities"…',
  isSearching = false,
}: SearchBarProps) {
  const [local, setLocal] = useState(value)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Sync if parent resets value
  useEffect(() => { setLocal(value) }, [value])

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const v = e.target.value
    setLocal(v)
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => onChange(v), 500)
  }

  function handleClear() {
    setLocal('')
    onChange('')
  }

  return (
    <div className="relative w-full">
      {/* Search icon */}
      <div className="pointer-events-none absolute inset-y-0 left-4 flex items-center">
        {isSearching ? (
          <svg className="w-5 h-5 text-primary-500 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-secondary-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
        )}
      </div>

      <input
        type="search"
        value={local}
        onChange={handleChange}
        placeholder={placeholder}
        aria-label="Search events"
        className="w-full pl-12 pr-10 py-3 rounded-xl border border-secondary-200 bg-white text-secondary-900 placeholder:text-secondary-400 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent transition"
      />

      {/* Clear button */}
      {local && (
        <button
          type="button"
          onClick={handleClear}
          aria-label="Clear search"
          className="absolute inset-y-0 right-3 flex items-center text-secondary-400 hover:text-secondary-600 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}
