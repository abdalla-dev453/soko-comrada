import { PackageSearch } from "lucide-react";

import { GigCard } from "./GigCard";
import { GigFilters } from "./GigFilters";
import { GigFeedSkeleton } from "../common/Skeleton";
import { EmptyState } from "../common/EmptyState";
import { ErrorBanner } from "../common/ErrorBanner";
import { Button } from "../common/Button";
import { useGigs } from "../../hooks/useGigs";

export function GigFeed({ initialFilters }) {
  const {
    gigs,
    filters,
    updateFilters,
    resetFilters,
    page,
    setPage,
    totalPages,
    isLoading,
    isError,
    isEmpty,
    error,
    reload,
  } = useGigs(initialFilters);

  return (
    <div>
      <GigFilters filters={filters} onChange={updateFilters} onReset={resetFilters} />

      <div className="mt-6">
        {isLoading && <GigFeedSkeleton />}

        {isError && (
          <ErrorBanner
            title="Couldn't load gigs"
            message={error?.message || "Check your connection and try again."}
            onDismiss={reload}
          />
        )}

        {isEmpty && (
          <EmptyState
            icon={PackageSearch}
            title="No gigs match those filters yet"
            description="Try widening your search, or be the first to post one for your campus."
            action={
              <Button as="a" href="/gigs/new" variant="secondary">
                Post a gig
              </Button>
            }
          />
        )}

        {!isLoading && !isError && gigs.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {gigs.map((gig) => (
              <GigCard key={gig.id} gig={gig} />
            ))}
          </div>
        )}
      </div>

      {totalPages > 1 && !isLoading && (
        <div className="mt-8 flex items-center justify-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Previous
          </Button>
          <span className="text-fluid-sm text-ink-muted">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="secondary"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}