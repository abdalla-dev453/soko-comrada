import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, CheckCircle2, XCircle, PartyPopper, Star, UserPlus } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { SectionLoader } from "../components/common/Loader";
import { EmptyState } from "../components/common/EmptyState";
import { apiClient } from "../api/client";

const ICONS = {
  new_application: UserPlus,
  application_accepted: CheckCircle2,
  application_rejected: XCircle,
  gig_completed: PartyPopper,
  review_received: Star,
};

export default function Notifications() {
  const [items, setItems] = useState(null);

  useEffect(() => {
    apiClient
      .get("/auth/notifications")
      .then((data) => setItems(data.notifications))
      .catch(() => setItems([]));
  }, []);

  return (
    <>
      <SEO title="Notifications" description="Recent activity on your gigs and applications." path="/notifications" noindex />

      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        <h1 className="font-display font-semibold text-fluid-2xl mb-6">Notifications</h1>

        {items === null && <SectionLoader label="Loading notifications…" />}

        {items && items.length === 0 && (
          <EmptyState
            icon={Bell}
            title="Nothing new yet"
            description="Applications, acceptances, and reviews on your gigs will show up here."
          />
        )}

        {items && items.length > 0 && (
          <ul className="flex flex-col divide-y divide-border rounded-lg border border-border bg-surface">
            {items.map((item, i) => {
              const Icon = ICONS[item.type] || Bell;
              return (
                <li key={i} className="flex items-start gap-3 p-4">
                  <Icon className="h-5 w-5 flex-shrink-0 text-moss-strong mt-0.5" aria-hidden="true" />
                  <div className="flex-1 min-w-0">
                    <p className="text-fluid-sm text-ink">{item.message}</p>
                    <p className="mt-0.5 text-fluid-xs text-ink-muted">
                      {new Date(item.created_at).toLocaleString("en-KE", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })}
                    </p>
                  </div>
                  {item.gig_id && (
                    <Link
                      to={`/gigs/${item.gig_id}`}
                      className="flex-shrink-0 text-fluid-xs text-ink underline decoration-dotted"
                    >
                      View
                    </Link>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </>
  );
}