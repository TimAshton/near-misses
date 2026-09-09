import type {
  Incident,
  IncidentListResponse,
  IncidentFilters,
  Stats,
  StatsWindow,
  PollTriggerResponse,
} from "./types";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Request failed: ${res.status} ${res.statusText} ${body}`);
  }
  return res.json() as Promise<T>;
}

function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function fetchIncidents(filters: IncidentFilters = {}): Promise<IncidentListResponse> {
  const qs = buildQuery({
    category: filters.category,
    severity: filters.severity,
    state: filters.state,
    date_from: filters.date_from,
    date_to: filters.date_to,
    limit: filters.limit,
    offset: filters.offset,
    sort: filters.sort,
    order: filters.order,
  });
  return request<IncidentListResponse>(`/api/incidents${qs}`);
}

export function fetchIncident(id: string): Promise<Incident> {
  return request<Incident>(`/api/incidents/${id}`);
}

export function fetchStats(window: StatsWindow = "24h"): Promise<Stats> {
  return request<Stats>(`/api/stats${buildQuery({ window })}`);
}

export function triggerPoll(): Promise<PollTriggerResponse> {
  return request<PollTriggerResponse>("/api/poll/trigger", { method: "POST" });
}

export function exportCsvUrl(filters: IncidentFilters = {}): string {
  const qs = buildQuery({
    category: filters.category,
    severity: filters.severity,
    state: filters.state,
    date_from: filters.date_from,
    date_to: filters.date_to,
    sort: filters.sort,
    order: filters.order,
  });
  return `${API_URL}/api/incidents/export.csv${qs}`;
}
