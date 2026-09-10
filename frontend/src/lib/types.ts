export type Category = "aviation" | "rail" | "seismic" | "tsunami" | "hurricane" | "wildfire";

export type Severity = "low" | "medium" | "high" | "critical";

export interface IncidentLocation {
  lat: number;
  lng: number;
  city: string | null;
  state: string | null;
  display_name: string;
}

export interface Incident {
  id: string;
  source: string;
  category: Category;
  event_type: string;
  severity: Severity;
  title: string;
  description: string;
  occurred_at: string; // ISO8601
  ingested_at: string; // ISO8601
  location: IncidentLocation;
  source_url: string;
  raw: Record<string, unknown>;
}

export interface IncidentListResponse {
  items: Incident[];
  total: number;
  limit: number;
  offset: number;
}

export interface IncidentFilters {
  category?: Category;
  severity?: Severity;
  state?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
  sort?: string;
  order?: "asc" | "desc";
}

export type StatsWindow = "24h" | "7d" | "30d";

export interface TimelinePoint {
  bucket: string; // ISO8601 date/time bucket
  count: number;
}

export interface StateCount {
  state: string;
  count: number;
}

export interface Stats {
  total_incidents: number;
  last_updated: string | null;
  by_category: Record<string, number>;
  by_severity: Record<string, number>;
  top_states: StateCount[];
  timeline: TimelinePoint[];
  window: StatsWindow;
}

export interface PollTriggerResponse {
  new_incidents: number;
  triggered_at: string;
}
