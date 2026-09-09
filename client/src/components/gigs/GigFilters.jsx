import { SlidersHorizontal, X } from "lucide-react";

import { fieldClasses } from "../common/ErrorBanner";

const CATEGORIES = [
  "writing",
  "cleaning",
  "tech help",
  "tutoring",
  "printing",
  "beauty",
  "errands",
  "design",
  "photography",
  "moving help",
];

export function GigFilters({ filters, onChange, onReset }) {
  const hasActiveFilters = Object.values(filters).some((v) => v);

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="flex flex-col gap-1 min-w-[10rem]">
        <label htmlFor="filter-campus" className="text-fluid-xs font-medium text-ink-muted">
          Campus
        </label>
        <input
          id="filter-campus"
          type="text"
          placeholder="e.g. JKUAT Juja"
          value={filters.campus}
          onChange={(e) => onChange({ campus: e.target.value })}
          className={fieldClasses(false)}
        />
      </div>

      <div className="flex flex-col gap-1 min-w-[9rem]">
        <label htmlFor="filter-category" className="text-fluid-xs font-medium text-ink-muted">
          Category
        </label>
        <select
          id="filter-category"
          value={filters.category}
          onChange={(e) => onChange({ category: e.target.value })}
          className={fieldClasses(false)}
        >
          <option value="">Any category</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c[0].toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1 min-w-[8rem]">
        <label htmlFor="filter-type" className="text-fluid-xs font-medium text-ink-muted">
          Type
        </label>
        <select
          id="filter-type"
          value={filters.type}
          onChange={(e) => onChange({ type: e.target.value })}
          className={fieldClasses(false)}
        >
          <option value="">Task or skill</option>
          <option value="TASK_NEEDED">Task needed</option>
          <option value="SKILL_OFFERED">Skill offered</option>
        </select>
      </div>

      <label className="flex items-center gap-2 pb-2.5 text-fluid-sm text-ink cursor-pointer select-none">
        <input
          type="checkbox"
          checked={filters.urgent === "true"}
          onChange={(e) => onChange({ urgent: e.target.checked ? "true" : "" })}
          className="h-4 w-4 rounded border-border text-coral focus:ring-coral/40"
        />
        Urgent only
      </label>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={onReset}
          className="flex items-center gap-1 pb-2.5 text-fluid-sm text-ink-muted hover:text-ink transition-colors"
        >
          <X className="h-4 w-4" aria-hidden="true" />
          Clear filters
        </button>
      )}

      <span className="hidden lg:inline-flex items-center gap-1.5 pb-2.5 ml-auto text-fluid-xs text-ink-muted">
        <SlidersHorizontal className="h-3.5 w-3.5" aria-hidden="true" />
        Boosted gigs show first
      </span>
    </div>
  );
}