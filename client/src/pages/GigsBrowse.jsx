import { SEO } from "../components/common/SEO";
import { GigFeed } from "../components/gigs/GigFeed";

export default function GigsBrowse() {
  return (
    <>
      <SEO
        title="Browse gigs"
        description="Browse open tasks and skills on offer across campus — filter by category, campus, and urgency."
        path="/gigs"
      />
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="mb-8">
          <h1 className="font-display font-semibold text-fluid-2xl">Open gigs</h1>
          <p className="mt-1 text-fluid-sm text-ink-muted">
            Boosted gigs show first, then newest. Filter to your campus to see what's
            actually reachable.
          </p>
        </div>
        <GigFeed />
      </div>
    </>
  );
}