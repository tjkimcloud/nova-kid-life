export function EventCardSkeleton() {
  return (
    <div className="flex flex-col rounded-2xl overflow-hidden bg-white shadow-sm border border-secondary-100 animate-pulse">
      {/* Image placeholder */}
      <div className="w-full bg-secondary-100" style={{ paddingBottom: '66.67%' }} />

      {/* Content */}
      <div className="flex flex-col gap-3 p-4">
        {/* Date row */}
        <div className="flex justify-between items-center">
          <div className="h-3 w-32 rounded bg-secondary-100" />
          <div className="h-5 w-12 rounded-full bg-secondary-100" />
        </div>
        {/* Title */}
        <div className="space-y-1.5">
          <div className="h-4 w-full rounded bg-secondary-100" />
          <div className="h-4 w-3/4 rounded bg-secondary-100" />
        </div>
        {/* Location */}
        <div className="h-3 w-40 rounded bg-secondary-100" />
        {/* Tags */}
        <div className="flex gap-1 pt-1">
          <div className="h-5 w-14 rounded-full bg-secondary-100" />
          <div className="h-5 w-16 rounded-full bg-secondary-100" />
        </div>
      </div>
    </div>
  )
}

export function EventGridSkeleton({ count = 9 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <EventCardSkeleton key={i} />
      ))}
    </div>
  )
}
