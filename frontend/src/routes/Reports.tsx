import { useState } from "react";
import { PageShell } from "../components/layout/PageShell";
import { IncidentTable } from "../components/reports/IncidentTable";
import { CsvExportButton } from "../components/reports/CsvExportButton";
import { FilterPanel } from "../components/map/FilterPanel";
import { useIncidents } from "../hooks/useIncidents";
import type { IncidentFilters } from "../lib/types";

export function Reports() {
  const [filters, setFilters] = useState<IncidentFilters>({
    limit: 100,
    sort: "occurred_at",
    order: "desc",
  });
  const { incidents, total, loading, error } = useIncidents(filters);

  function handleSortChange(sort: string, order: "asc" | "desc") {
    setFilters((prev) => ({ ...prev, sort, order }));
  }

  return (
    <PageShell title="Reports" actions={<CsvExportButton filters={filters} />}>
      <div className="mb-4 rounded-lg border border-gray-800 bg-gray-900 p-4">
        <FilterPanel filters={filters} onChange={setFilters} variant="inline" />
      </div>

      {loading && <p className="text-gray-400">Loading…</p>}
      {error && <p className="text-red-400">{error}</p>}
      {!loading && !error && (
        <>
          <p className="mb-2 text-sm text-gray-500" data-testid="incident-count">
            {total} incidents
          </p>
          <IncidentTable incidents={incidents} filters={filters} onSortChange={handleSortChange} />
        </>
      )}
    </PageShell>
  );
}
