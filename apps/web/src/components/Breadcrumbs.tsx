import Link from 'next/link'

export interface BreadcrumbItem {
  name: string
  href?: string
}

interface Props {
  items: BreadcrumbItem[]
}

export function Breadcrumbs({ items }: Props) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1 text-sm text-secondary-500">
        {items.map((item, i) => {
          const isLast = i === items.length - 1
          return (
            <li key={i} className="flex items-center gap-1">
              {i > 0 && (
                <svg
                  className="w-3.5 h-3.5 shrink-0 text-secondary-300"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
              {isLast || !item.href ? (
                <span
                  className={isLast ? 'text-secondary-700 font-medium truncate max-w-[200px] sm:max-w-xs' : ''}
                  aria-current={isLast ? 'page' : undefined}
                >
                  {item.name}
                </span>
              ) : (
                <Link
                  href={item.href}
                  className="hover:text-primary-600 transition-colors whitespace-nowrap"
                >
                  {item.name}
                </Link>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
