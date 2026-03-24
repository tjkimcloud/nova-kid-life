// Skeleton that matches the new list row layout (no image)

function EventRowSkeleton() {
  return (
    <div className="flex items-start gap-3 px-4 py-3.5 animate-pulse">
      {/* Time */}
      <div className="shrink-0 w-[64px] h-3 rounded bg-secondary-100 mt-1" />
      {/* Content */}
      <div className="flex-1 space-y-2">
        <div className="h-3.5 w-3/4 rounded bg-secondary-100" />
        <div className="flex gap-1.5">
          <div className="h-3 w-28 rounded bg-secondary-100" />
          <div className="h-3 w-14 rounded-full bg-secondary-100" />
        </div>
      </div>
      {/* Price */}
      <div className="shrink-0 h-3 w-10 rounded bg-secondary-100" />
    </div>
  )
}

export function EventCardSkeleton() {
  return <EventRowSkeleton />
}

export function EventGridSkeleton({ count = 12 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {/* Simulate two date groups */}
      {[0, 1].map(g => (
        <div
          key={g}
          className="overflow-hidden border border-secondary-100 bg-white"
          style={{ borderRadius: '16px' }}
        >
          <div className="px-4 py-2.5 border-b border-secondary-100 flex items-center justify-between bg-secondary-50/60 animate-pulse">
            <div className="h-3 w-24 rounded bg-secondary-100" />
            <div className="h-3 w-12 rounded bg-secondary-100" />
          </div>
          <div className="divide-y divide-secondary-50">
            {Array.from({ length: Math.ceil(count / 2) }).map((_, i) => (
              <EventRowSkeleton key={i} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
