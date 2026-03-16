import Link from 'next/link'

const NAV_LINKS = [
  { href: '/events',  label: 'Events' },
  { href: '/pokemon', label: 'Pokémon TCG' },
]

export function Header() {
  return (
    <header className="bg-white border-b border-secondary-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 shrink-0"
            aria-label="NovaKidLife — Home"
          >
            <span className="font-heading font-extrabold text-xl text-primary-600 leading-none">
              Nova<span className="text-secondary-700">Kid</span>Life
            </span>
          </Link>

          {/* Desktop nav */}
          <nav aria-label="Main navigation">
            <ul className="flex items-center gap-1">
              {NAV_LINKS.map(({ href, label }) => (
                <li key={href}>
                  <Link
                    href={href}
                    className="px-4 py-2 rounded-lg text-sm font-semibold text-secondary-600 hover:text-primary-600 hover:bg-primary-50 transition-colors"
                  >
                    {label}
                  </Link>
                </li>
              ))}
              <li>
                <Link
                  href="/events"
                  className="ml-2 px-4 py-2 rounded-lg text-sm font-semibold bg-primary-500 text-white hover:bg-primary-600 transition-colors"
                >
                  Find Events
                </Link>
              </li>
            </ul>
          </nav>

        </div>
      </div>
    </header>
  )
}
