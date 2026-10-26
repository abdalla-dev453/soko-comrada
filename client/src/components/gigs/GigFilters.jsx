import { SlidersHorizontal, X, Search } from "lucide-react";
import { fieldClasses } from "../common/ErrorBanner";

const CATEGORIES = [
  "gigs_work",
  "tutoring",
  "tech help",
  "design",
  "writing",
  "delivery",
  "photography",
  "errands",
  "events",
  "cleaning",
  "campus ambassador",
  "internship",
];

export function GigFilters({ filters, onChange, onReset }) {
  const hasActiveFilters = Object.values(filters).some((v) => v);

  return (
    <div className="flex flex-col gap-3">
      {/* Keyword Search Row */}
      <div className="relative w-full">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-muted" />
        <input
          type="text"
          placeholder="Search by keywords (e.g. Python, design, Calculus, hostel)..."
          value={filters.q || ""}
          onChange={(e) => onChange({ q: e.target.value })}
          className={`${fieldClasses(false)} pl-9 w-full`}
        />
      </div>

      <div className="flex flex-wrap items-end gap-3">
        <div className="flex flex-col gap-1 min-w-[9rem]">
          <label htmlFor="filter-campus" className="text-xs font-medium text-ink-muted">
            Campus
          </label>
          <input
            id="filter-campus"
            type="text"
            placeholder="e.g. UoN Main, JKUAT Juja"
            value={filters.campus || ""}
            onChange={(e) => onChange({ campus: e.target.value })}
            className={fieldClasses(false)}
          />
        </div>

        <div className="flex flex-col gap-1 min-w-[9rem]">
          <label htmlFor="filter-category" className="text-xs font-medium text-ink-muted">
            Category
          </label>
          <select
            id="filter-category"
            value={filters.category || ""}
            onChange={(e) => onChange({ category: e.target.value })}
            className={fieldClasses(false)}
          >
            <option value="">Any category</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c.replace("_", " ").toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1 min-w-[8rem]">
          <label htmlFor="filter-work-arrangement" className="text-xs font-medium text-ink-muted">
            Work Mode
          </label>
          <select
            id="filter-work-arrangement"
            value={filters.work_arrangement || ""}
            onChange={(e) => onChange({ work_arrangement: e.target.value })}
            className={fieldClasses(false)}
          >
            <option value="">Any work mode</option>
            <option value="ON_SITE">On Campus</option>
            <option value="REMOTE">Remote</option>
            <option value="HYBRID">Hybrid</option>
          </select>
        </div>

        <div className="flex flex-col gap-1 min-w-[8rem]">
          <label htmlFor="filter-sort" className="text-xs font-medium text-ink-muted">
            Sort by
          </label>
          <select
            id="filter-sort"
            value={filters.sort || ""}
            onChange={(e) => onChange({ sort: e.target.value })}
            className={fieldClasses(false)}
          >
            <option value="">Newest first</option>
            <option value="highest_pay">Highest pay</option>
            <option value="closest_deadline">Closest deadline</option>
            <option value="oldest">Oldest</option>
          </select>
        </div>

        <label className="flex items-center gap-2 pb-2.5 text-sm text-ink cursor-pointer select-none">
          <input
            type="checkbox"
            checked={filters.urgent === "true"}
            onChange={(e) => onChange({ urgent: e.target.checked ? "true" : "" })}
            className="h-4 w-4 rounded border-border text-accent focus:ring-accent/20"
          />
          Urgent only
        </label>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={onReset}
            className="flex items-center gap-1 pb-2.5 text-sm text-ink-muted hover:text-ink transition-colors"
          >
            <X className="h-4 w-4" aria-hidden="true" />
            Clear filters
          </button>
        )}

        <span className="hidden lg:inline-flex items-center gap-1.5 pb-2.5 ml-auto text-xs text-ink-muted">
          <SlidersHorizontal className="h-3.5 w-3.5" aria-hidden="true" />
          Boosted gigs show first
        </span>
      </div>
    </div>
  );
}
