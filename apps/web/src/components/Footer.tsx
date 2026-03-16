import Link from 'next/link'

const SITE_LINKS = [
  { href: '/events',          label: 'Family Events' },
  { href: '/pokemon',         label: 'Pokémon TCG' },
  { href: '/about',           label: 'About' },
  { href: '/privacy-policy',  label: 'Privacy Policy' },
]

const SOCIAL_LINKS = [
  {
    href:  'https://twitter.com/novakidlife',
    label: 'Follow NovaKidLife on X (Twitter)',
    icon:  (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5" aria-hidden="true">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.259 5.63L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z" />
      </svg>
    ),
  },
  {
    href:  'https://instagram.com/novakidlife',
    label: 'Follow NovaKidLife on Instagram',
    icon:  (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5" aria-hidden="true">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
      </svg>
    ),
  },
  {
    href:  'https://facebook.com/novakidlife',
    label: 'Follow NovaKidLife on Facebook',
    icon:  (
      <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5" aria-hidden="true">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
      </svg>
    ),
  },
]

export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="bg-secondary-900 text-secondary-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-secondary-700">

          {/* Brand */}
          <div>
            <p className="font-heading font-extrabold text-xl text-white mb-2">
              Nova<span className="text-primary-400">Kid</span>Life
            </p>
            <p className="text-sm text-secondary-400 leading-relaxed">
              Northern Virginia&rsquo;s most complete family events calendar.
              Updated daily from 59+ local sources — completely free.
            </p>
            <div className="flex gap-3 mt-4">
              {SOCIAL_LINKS.map(({ href, label, icon }) => (
                <a
                  key={href}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="text-secondary-400 hover:text-primary-400 transition-colors"
                >
                  {icon}
                </a>
              ))}
            </div>
          </div>

          {/* Coverage */}
          <div>
            <h2 className="font-heading font-bold text-sm uppercase tracking-wider text-secondary-400 mb-3">
              Coverage Area
            </h2>
            <ul className="space-y-1 text-sm">
              {['Fairfax County', 'Loudoun County', 'Arlington County', 'Prince William County'].map((c) => (
                <li key={c}>{c}, Virginia</li>
              ))}
            </ul>
          </div>

          {/* Links */}
          <div>
            <h2 className="font-heading font-bold text-sm uppercase tracking-wider text-secondary-400 mb-3">
              Explore
            </h2>
            <ul className="space-y-2 text-sm">
              {SITE_LINKS.map(({ href, label }) => (
                <li key={href}>
                  <a
                    href={href}
                    className="hover:text-primary-400 transition-colors"
                  >
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

        </div>

        <p className="pt-6 text-xs text-secondary-500 text-center">
          &copy; {year} NovaKidLife. All rights reserved. Not affiliated with any county government or event organizer.
        </p>

      </div>
    </footer>
  )
}
