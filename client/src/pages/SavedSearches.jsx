import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bell, BookmarkPlus, Search, Trash2 } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import {
  getAlertPreferences,
  getSavedSearches,
  removeSavedSearch,
  setAlertPreferences,
} from "../utils/savedSearches";

export default function SavedSearches() {
  const navigate = useNavigate();
  const [searches, setSearches] = useState([]);
  const [alertPreferences, setAlertPreferencesState] = useState(getAlertPreferences());

  useEffect(() => {
    setSearches(getSavedSearches());
    setAlertPreferencesState(getAlertPreferences());
  }, []);

  const refreshSavedSearches = () => {
    setSearches(getSavedSearches());
  };

  const toggleAlert = (key) => {
    const next = { ...alertPreferences, [key]: !alertPreferences[key] };
    setAlertPreferencesState(next);
    setAlertPreferences(next);
  };

  return (
    <>
      <SEO
        title="Saved searches"
        description="Saved gig searches and alert preferences for faster campus discovery."
        path="/saved-searches"
        noindex
      />

      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="font-display font-semibold text-2xl">Saved searches</h1>
            <p className="text-sm text-ink-muted">
              Save the filters you use most and decide which alerts you want to receive.
            </p>
          </div>
          <Button as={Link} to="/gigs" icon={Search} variant="secondary">
            Browse gigs
          </Button>
        </div>

        <div className="grid gap-5 lg:grid-cols-[1.35fr,0.65fr]">
          <div className="rounded-card border border-border bg-surface-raised p-5 shadow-card">
            <div className="mb-4 flex items-center gap-2 text-sm font-medium text-ink">
              <BookmarkPlus className="h-4 w-4 text-accent" aria-hidden="true" />
              Your saved filters
            </div>

            {searches.length === 0 ? (
              <EmptyState
                icon={Search}
                title="No saved searches yet"
                description="Save a campus search while browsing gigs to come back to it faster."
              />
            ) : (
              <ul className="space-y-3">
                {searches.map((search) => {
                  const summaryParts = [];
                  if (search.filters?.campus) summaryParts.push(search.filters.campus);
                  if (search.filters?.category) summaryParts.push(search.filters.category);
                  if (search.filters?.type) summaryParts.push(search.filters.type);
                  if (search.filters?.urgent === "true") summaryParts.push("Urgent only");

                  return (
                    <li
                      key={search.id}
                      className="rounded-lg border border-border bg-surface p-3"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-medium text-ink">{search.name}</p>
                          <p className="mt-1 text-xs text-ink-muted">
                            {summaryParts.length ? summaryParts.join(" · ") : "Any open gigs"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => navigate("/gigs", { state: { savedFilters: search.filters } })}
                          >
                            Load
                          </Button>
                          <button
                            type="button"
                            onClick={() => {
                              removeSavedSearch(search.id);
                              refreshSavedSearches();
                            }}
                            className="rounded-md p-2 text-ink-muted transition hover:bg-muted hover:text-ink"
                            aria-label={`Remove ${search.name}`}
                          >
                            <Trash2 className="h-4 w-4" aria-hidden="true" />
                          </button>
                        </div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div className="rounded-card border border-border bg-surface-raised p-5 shadow-card">
            <div className="mb-4 flex items-center gap-2 text-sm font-medium text-ink">
              <Bell className="h-4 w-4 text-success" aria-hidden="true" />
              Alert preferences
            </div>

            <div className="space-y-3">
              <label className="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-border bg-surface p-3 text-sm text-ink">
                <span>Matching gig alerts</span>
                <input
                  type="checkbox"
                  checked={Boolean(alertPreferences.matchingGigs)}
                  onChange={() => toggleAlert("matchingGigs")}
                  className="h-4 w-4 rounded border-border text-accent focus:ring-accent/20"
                />
              </label>

              <label className="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-border bg-surface p-3 text-sm text-ink">
                <span>Application updates</span>
                <input
                  type="checkbox"
                  checked={Boolean(alertPreferences.applicationUpdates)}
                  onChange={() => toggleAlert("applicationUpdates")}
                  className="h-4 w-4 rounded border-border text-accent focus:ring-accent/20"
                />
              </label>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
