'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

const LOCATIONS = [
  'Northern Virginia', 'Fairfax', 'Reston', 'Chantilly', 'Herndon',
  'McLean', 'Vienna', 'Leesburg', 'Ashburn', 'Sterling',
  'Manassas', 'Arlington', 'Alexandria', 'Springfield', 'Centreville',
]

const DATE_OPTIONS = [
  { label: 'This Weekend', value: 'weekend' },
  { label: 'Today',        value: 'today'   },
  { label: 'Tomorrow',     value: 'tomorrow' },
  { label: 'This Week',    value: 'week'    },
  { label: 'This Month',   value: 'month'   },
]

const AGE_OPTIONS = [
  { label: 'All Ages',          value: '',        ageMin: '', ageMax: '' },
  { label: 'Toddlers (0–3)',    value: 'toddler', ageMin: '0', ageMax: '3' },
  { label: 'Little Kids (4–7)', value: 'little',  ageMin: '4', ageMax: '7' },
  { label: 'Big Kids (8–12)',   value: 'big',     ageMin: '8', ageMax: '12' },
  { label: 'Teens (13+)',       value: 'teen',    ageMin: '13', ageMax: '' },
]

const DAY_LABELS  = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
// Placeholder counts — replace with API aggregate endpoint in Session 12
const DAY_COUNTS  = [8, 5, 6, 9, 14, 24, 18]

function toISO(d: Date) {
  return d.toISOString().split('T')[0]
}

function getWeekDays(): Date[] {
  const today  = new Date()
  const dow    = today.getDay()
  const monday = new Date(today)
  monday.setDate(today.getDate() - (dow === 0 ? 6 : dow - 1))
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    return d
  })
}

export function HeroSearch() {
  const router   = useRouter()
  const [loc,    setLoc]    = useState('Northern Virginia')
  const [date,   setDate]   = useState('weekend')
  const [ageVal, setAgeVal] = useState('')

  const weekDays = getWeekDays()
  const todayStr = toISO(new Date())

  function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    const p = new URLSearchParams()
    if (date) p.set('date', date)
    const ageOpt = AGE_OPTIONS.find(a => a.value === ageVal)
    if (ageOpt?.ageMin) p.set('age_min', ageOpt.ageMin)
    if (ageOpt?.ageMax) p.set('age_max', ageOpt.ageMax)
    if (loc && loc !== 'Northern Virginia') p.set('q', loc)
    router.push(`/events${p.size ? `?${p}` : ''}`)
  }

  function goDay(d: Date) {
    const s = toISO(d)
    router.push(`/events?date_from=${s}&date_to=${s}`)
  }

  return (
    <div className="w-full space-y-4">

      {/* ── Search card ── */}
      <form
        onSubmit={handleSearch}
        className="bg-white rounded-2xl shadow-xl border border-secondary-100 overflow-hidden"
      >
        <div className="flex flex-col lg:flex-row divide-y lg:divide-y-0 lg:divide-x divide-secondary-100">

          <div className="flex-1 px-5 py-4">
            <label className="block text-[10px] font-bold text-secondary-400 uppercase tracking-widest mb-1.5">
              Location
            </label>
            <select
              value={loc}
              onChange={e => setLoc(e.target.value)}
              className="w-full text-secondary-900 font-semibold text-sm bg-transparent focus:outline-none cursor-pointer"
            >
              {LOCATIONS.map(l => <option key={l}>{l}</option>)}
            </select>
          </div>

          <div className="flex-1 px-5 py-4">
            <label className="block text-[10px] font-bold text-secondary-400 uppercase tracking-widest mb-1.5">
              When
            </label>
            <select
              value={date}
              onChange={e => setDate(e.target.value)}
              className="w-full text-secondary-900 font-semibold text-sm bg-transparent focus:outline-none cursor-pointer"
            >
              {DATE_OPTIONS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>

          <div className="flex-1 px-5 py-4">
            <label className="block text-[10px] font-bold text-secondary-400 uppercase tracking-widest mb-1.5">
              Age Group
            </label>
            <select
              value={ageVal}
              onChange={e => setAgeVal(e.target.value)}
              className="w-full text-secondary-900 font-semibold text-sm bg-transparent focus:outline-none cursor-pointer"
            >
              {AGE_OPTIONS.map(a => <option key={a.value} value={a.value}>{a.label}</option>)}
            </select>
          </div>

          <div className="flex items-center px-5 py-4">
            <button
              type="submit"
              className="w-full lg:w-auto inline-flex items-center justify-center gap-2 px-7 py-3 rounded-xl bg-primary-500 text-white font-bold text-sm hover:bg-primary-600 active:bg-primary-700 transition-colors whitespace-nowrap shadow-sm"
            >
              Find Events
              <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M3 10a.75.75 0 01.75-.75h10.638L10.23 5.29a.75.75 0 111.04-1.08l5.5 5.25a.75.75 0 010 1.08l-5.5 5.25a.75.75 0 11-1.04-1.08l4.158-3.96H3.75A.75.75 0 013 10z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </form>

      {/* ── Quick filter pills ── */}
      <div className="flex flex-wrap gap-2">
        {[
          { label: '🔥 Happening Today',  href: '/events?date=today'   },
          { label: '🗓️ This Weekend',      href: '/events?date=weekend' },
          { label: '🆓 Free Events Only', href: '/events?free=true'    },
        ].map(({ label, href }) => (
          <a
            key={href}
            href={href}
            className="inline-flex items-center px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-white/60 text-secondary-700 text-sm font-semibold hover:bg-white hover:border-primary-300 hover:text-primary-700 transition-all shadow-sm"
          >
            {label}
          </a>
        ))}
      </div>

      {/* ── Weekly calendar strip ── */}
      <div className="flex gap-1.5 overflow-x-auto">
        {weekDays.map((day, i) => {
          const dateStr = toISO(day)
          const isToday = dateStr === todayStr
          const isPast  = day < new Date(new Date().setHours(0, 0, 0, 0))
          return (
            <button
              key={dateStr}
              onClick={() => !isPast && goDay(day)}
              disabled={isPast}
              className={`flex-1 min-w-[48px] flex flex-col items-center py-2.5 rounded-xl text-center transition-all ${
                isToday
                  ? 'bg-primary-500 text-white shadow-md scale-105'
                  : isPast
                  ? 'bg-white/30 text-white/30 cursor-not-allowed'
                  : 'bg-white/60 backdrop-blur-sm text-white hover:bg-white hover:text-secondary-900 hover:scale-105'
              }`}
            >
              <span className="text-[10px] font-bold uppercase tracking-wide">{DAY_LABELS[i]}</span>
              <span className="text-lg font-extrabold font-heading leading-tight">{day.getDate()}</span>
              <span className={`text-[10px] font-semibold ${isToday ? 'text-white/70' : isPast ? 'opacity-0' : 'text-primary-200'}`}>
                {DAY_COUNTS[i]}
              </span>
            </button>
          )
        })}
      </div>

      {/* ── Social proof ── */}
      <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-sm">
        <span className="text-white/70">🔥 <span className="font-bold text-white">24 events</span> this weekend</span>
        <span className="hidden sm:block text-white/30">·</span>
        <span className="text-white/70">⭐ Trusted by <span className="font-bold text-white">4,200+</span> NoVa families</span>
        <span className="hidden sm:block text-white/30">·</span>
        <span className="text-white/70">🆓 <span className="font-bold text-white">Always free</span></span>
      </div>

    </div>
  )
}
