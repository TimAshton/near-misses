import { daysAgoFromIsoDate, isoDateDaysAgo } from "../../lib/formatters";
import type { Category, IncidentFilters, Severity } from "../../lib/types";

// Slider covers the last two years day-by-day; anything older is still
// reachable by typing an exact date into the "From" field below it.
const MAX_SLIDER_DAYS = 730;

const CATEGORIES: Category[] = [
  "aviation",
  "rail",
  "seismic",
  "tsunami",
  "hurricane",
  "wildfire",
  "maritime",
  "severe_weather",
];
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

  // Slider position increases left-to-right toward "today", so it reads
  // left (further back) -> right (present) like a timeline. Unset date_from
  // defaults to yesterday rather than the oldest end.
  const daysAgo = filters.date_from ? daysAgoFromIsoDate(filters.date_from, MAX_SLIDER_DAYS) : 1;
  const sliderValue = MAX_SLIDER_DAYS - daysAgo;

  function setDateFromDaysAgo(sliderPos: number) {
    onChange({ ...filters, date_from: isoDateDaysAgo(MAX_SLIDER_DAYS - sliderPos) });
  }

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

      <div className={variant === "overlay" ? "" : "w-full sm:w-64"}>
        <label className="mb-1 flex items-center justify-between text-xs font-medium uppercase text-gray-400">
          <span>Search start</span>
          <span className="normal-case text-gray-300">
            {filters.date_from
              ? new Date(`${filters.date_from}T00:00:00`).toLocaleDateString()
              : "Yesterday"}
          </span>
        </label>
        <input
          data-testid="filter-date-from-slider"
          type="range"
          min={0}
          max={MAX_SLIDER_DAYS}
          value={sliderValue}
          onChange={(e) => setDateFromDaysAgo(Number(e.target.value))}
          className="w-full accent-blue-500"
        />
        <div className="mb-2 flex justify-between text-[10px] text-gray-500">
          <span>{MAX_SLIDER_DAYS} days ago</span>
          <span>Today</span>
        </div>
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
