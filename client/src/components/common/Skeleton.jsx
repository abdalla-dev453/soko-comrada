import clsx from "clsx";

export function Skeleton({ className }) {
  return (
    <div
      className={clsx("animate-pulse rounded-md bg-ink/[0.06]", className)}
      aria-hidden="true"
    />
  );
}

export function GigCardSkeleton() {
  return (
    <div className="ticket bg-surface shadow-card pl-6 pr-4 py-4" style={{ "--spine": "rgb(var(--color-border))" }}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <Skeleton className="h-5 w-2/3" />
        <Skeleton className="h-5 w-14" />
      </div>
      <Skeleton className="h-3.5 w-full mb-2" />
      <Skeleton className="h-3.5 w-4/5 mb-4" />
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-16" />
      </div>
    </div>
  );
}

export function GigFeedSkeleton({ count = 6 }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" role="status" aria-label="Loading gigs">
      {Array.from({ length: count }).map((_, i) => (
        <GigCardSkeleton key={i} />
      ))}
    </div>
  );
}