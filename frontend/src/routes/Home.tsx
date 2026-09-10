import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchStats } from "../lib/api";
import type { Stats } from "../lib/types";
import { PageShell } from "../components/layout/PageShell";
import { StatTile } from "../components/dashboard/StatTile";
import { formatRelative } from "../lib/formatters";

export function Home() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetchStats("24h").then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <PageShell title="US Incident Map">
      <p className="mb-6 max-w-2xl text-gray-400">
        A large-screen dashboard overlaying publicly available US incident data — aviation, rail,
        seismic, tsunami, hurricane, and wildfire — onto an interactive map, polled from free
        public APIs and normalized to a shared schema.
      </p>

      <div className="mb-8 grid grid-cols-3 gap-4">
        <StatTile
          testId="stat-total"
          label="Total incidents"
          value={stats ? stats.total_incidents : "—"}
        />
        <StatTile
          testId="stat-last-updated"
          label="Last updated"
          value={stats?.last_updated ? formatRelative(stats.last_updated) : "—"}
        />
        <StatTile
          testId="stat-categories"
          label="Active categories"
          value={stats ? Object.keys(stats.by_category).length : "—"}
        />
      </div>

      <div className="flex gap-4">
        <Link
          to="/map"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500"
        >
          Open Map
        </Link>
        <Link
          to="/dashboard"
          className="rounded-md border border-gray-700 px-4 py-2 text-sm font-medium text-gray-200 hover:bg-gray-800"
        >
          Open Dashboard
        </Link>
      </div>
    </PageShell>
  );
}
