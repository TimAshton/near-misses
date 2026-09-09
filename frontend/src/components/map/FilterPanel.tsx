import type { Category, IncidentFilters, Severity } from "../../lib/types";

const CATEGORIES: Category[] = ["aviation", "rail", "seismic", "tsunami", "hurricane"];
const SEVERITIES: Severity[] = ["low", "medium", "high", "critical"];

interface FilterPanelProps {
  filters: IncidentFilters;
  onChange: (filters: IncidentFilters) => void;
  /** "overlay" floats over a map (default); "inline" fills its container in normal flow. */
  variant?: "overlay" | "inline";
}

export function FilterPanel({ filters, onChange, variant = "overlay" }: FilterPanelProps) {
  const wrapperClass =
    variant === "overlay"
      ? "absolute left-4 top-4 z-10 w-64 space-y-3 rounded-lg border border-gray-800 bg-gray-950/90 p-4 shadow-lg backdrop-blur"
      : "flex w-full flex-wrap items-end gap-4 space-y-0";

  return (
    <div data-testid="filter-panel" className={wrapperClass}>
      <div>
        <label className="mb-1 block text-xs font-medium uppercase text-gray-400">Category</label>
        <select
          data-testid="filter-category"
          className="w-full rounded border border-gray-700 bg-gray-900 px-2 py-1 text-sm text-gray-100"
          value={filters.category ?? ""}
          onChange={(e) =>
            onChange({ ...filters, category: (e.target.value || undefined) as Category | undefined })
          }
        >
          <option value="">All categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium uppercase text-gray-400">Severity</label>
        <select
          data-testid="filter-severity"
          className="w-full rounded border border-gray-700 bg-gray-900 px-2 py-1 text-sm text-gray-100"
          value={filters.severity ?? ""}
          onChange={(e) =>
            onChange({ ...filters, severity: (e.target.value || undefined) as Severity | undefined })
          }
        >
          <option value="">All severities</option>
          {SEVERITIES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="mb-1 block text-xs font-medium uppercase text-gray-400">From</label>
          <input
            data-testid="filter-date-from"
            type="date"
            className="w-full rounded border border-gray-700 bg-gray-900 px-2 py-1 text-sm text-gray-100"
            value={filters.date_from ?? ""}
            onChange={(e) => onChange({ ...filters, date_from: e.target.value || undefined })}
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium uppercase text-gray-400">To</label>
          <input
            data-testid="filter-date-to"
            type="date"
            className="w-full rounded border border-gray-700 bg-gray-900 px-2 py-1 text-sm text-gray-100"
            value={filters.date_to ?? ""}
            onChange={(e) => onChange({ ...filters, date_to: e.target.value || undefined })}
          />
        </div>
      </div>
    </div>
  );
}
