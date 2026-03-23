import Link from 'next/link'

const NAV_LINKS = [
  { href: '/events',  label: 'Events'      },
  { href: '/pokemon', label: 'Pokémon TCG' },
  { href: '/blog',    label: 'Guides'      },
]

export function Header() {
  return (
    <header
      className="sticky top-0 z-50 border-b border-secondary-200"
      style={{
        background:           'rgba(255,248,242,0.95)',
        backdropFilter:       'blur(14px)',
        WebkitBackdropFilter: 'blur(14px)',
      }}
    >
      <div className="max-w-5xl mx-auto px-5 lg:px-8 flex items-center justify-between h-14 lg:h-[60px]">

        {/* Logo — Nova (dark) · Kid (orange) · Life (dark) */}
        <Link
          href="/"
          className="shrink-0 font-heading font-extrabold text-[19px] lg:text-[21px] leading-none tracking-[-0.5px] text-secondary-900"
          aria-label="NovaKidLife — Home"
        >
          Nova<span className="text-primary-500">Kid</span>Life
        </Link>

        {/* Desktop nav links — hidden on mobile */}
        <nav aria-label="Main navigation" className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className="px-3 py-2 rounded-lg text-[14px] font-body font-medium text-secondary-500 hover:text-primary-500 transition-colors"
            >
              {label}
            </Link>
          ))}
        </nav>

        {/* CTA pill — always visible */}
        <Link
          href="/events"
          className="inline-flex items-center gap-1.5 text-[13px] font-body font-semibold text-white px-4 py-2 rounded-full shadow-orange hover:bg-primary-600 transition-colors"
          style={{ background: 'var(--orange)' }}
        >
          Find Events
        </Link>

      </div>
    </header>
  )
}
