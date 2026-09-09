import { useCallback, useState } from "react";
import { PageShell } from "../components/layout/PageShell";
import { IncidentMap } from "../components/map/IncidentMap";
import { FilterPanel } from "../components/map/FilterPanel";
import { IncidentPreviewModal } from "../components/map/IncidentPreviewModal";
import { useIncidents } from "../hooks/useIncidents";
import { useWebSocketIncidents } from "../hooks/useWebSocketIncidents";
import type { Incident, IncidentFilters } from "../lib/types";

export function MapPage() {
  const [filters, setFilters] = useState<IncidentFilters>({ limit: 500 });
  const { incidents, prependIncident } = useIncidents(filters);
  const [selected, setSelected] = useState<Incident | null>(null);

  useWebSocketIncidents(useCallback((incident) => prependIncident(incident), [prependIncident]));

  return (
    <PageShell title="Map" fullBleed>
      <div className="relative flex-1">
        <IncidentMap incidents={incidents} onSelect={setSelected} />
        <FilterPanel filters={filters} onChange={setFilters} />
        {selected && (
          <IncidentPreviewModal incident={selected} onClose={() => setSelected(null)} />
        )}
      </div>
    </PageShell>
  );
}
