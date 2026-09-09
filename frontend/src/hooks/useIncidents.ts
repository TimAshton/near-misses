import { useCallback, useEffect, useState } from "react";
import { fetchIncidents } from "../lib/api";
import type { Incident, IncidentFilters } from "../lib/types";

interface UseIncidentsResult {
  incidents: Incident[];
  total: number;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  prependIncident: (incident: Incident) => void;
}

export function useIncidents(filters: IncidentFilters = {}): UseIncidentsResult {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const filtersKey = JSON.stringify(filters);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchIncidents(filters)
      .then((res) => {
        setIncidents(res.items);
        setTotal(res.total);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtersKey]);

  useEffect(() => {
    load();
  }, [load]);

  const prependIncident = useCallback((incident: Incident) => {
    setIncidents((prev) => [incident, ...prev.filter((i) => i.id !== incident.id)]);
    setTotal((prev) => prev + 1);
  }, []);

  return { incidents, total, loading, error, refetch: load, prependIncident };
}
