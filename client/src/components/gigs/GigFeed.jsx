import { PackageSearch, BookmarkPlus } from "lucide-react";
import { useState } from "react";

import { GigCard } from "./GigCard";
import { GigFilters } from "./GigFilters";
import { GigFeedSkeleton } from "../common/Skeleton";
import { EmptyState } from "../common/EmptyState";
import { ErrorBanner } from "../common/ErrorBanner";
import { Button } from "../common/Button";
import { useGigs } from "../../hooks/useGigs";
import { upsertSavedSearch } from "../../utils/savedSearches";

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
  const [saveStatus, setSaveStatus] = useState("");

  const handleSaveCurrentSearch = () => {
    const suggestedName = [filters.campus, filters.category, filters.type]
      .filter(Boolean)
      .join(" / ") || "My campus search";

    const name = window.prompt("Name this saved search", suggestedName);
    if (!name) return;

    const result = upsertSavedSearch({ name, filters: { ...filters } });
    if (result) {
      setSaveStatus(`Saved “${result.name}”`);
    }
  };

  return (
    <div>
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <GigFilters filters={filters} onChange={updateFilters} onReset={resetFilters} />
        <Button
          type="button"
          variant="secondary"
          icon={BookmarkPlus}
          size="sm"
          onClick={handleSaveCurrentSearch}
          className="whitespace-nowrap"
        >
          Save search
        </Button>
      </div>

      {saveStatus && (
        <p className="mt-3 text-sm text-success">{saveStatus}</p>
      )}

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
          <span className="text-sm text-ink-muted">
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