import { useEffect, useState } from "react";
import { PageShell } from "../components/layout/PageShell";
import { StatTile } from "../components/dashboard/StatTile";
import { TimelineChart } from "../components/dashboard/TimelineChart";
import { SeverityBreakdown } from "../components/dashboard/SeverityBreakdown";
import { TopStatesTable } from "../components/dashboard/TopStatesTable";
import { RefreshButton } from "../components/dashboard/RefreshButton";
import { fetchStats } from "../lib/api";
import type { Stats, StatsWindow } from "../lib/types";
import { formatRelative } from "../lib/formatters";

const WINDOWS: StatsWindow[] = ["24h", "7d", "30d"];

export function Dashboard() {
  const [window_, setWindow] = useState<StatsWindow>("24h");
  const [stats, setStats] = useState<Stats | null>(null);

  function load() {
    fetchStats(window_).then(setStats).catch(() => setStats(null));
  }

  useEffect(load, [window_]);

  return (
    <PageShell
      title="Dashboard"
      actions={
        <div className="flex items-center gap-3">
          <div className="flex rounded-md border border-gray-700" data-testid="window-toggle">
            {WINDOWS.map((w) => (
              <button
                key={w}
                onClick={() => setWindow(w)}
                data-testid={`window-${w}`}
                className={`px-3 py-1.5 text-sm ${
                  window_ === w ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800"
                }`}
              >
                {w}
              </button>
            ))}
          </div>
          <RefreshButton onDone={load} />
        </div>
      }
    >
      <div className="mb-6 grid grid-cols-4 gap-4">
        <StatTile testId="stat-total" label="Total incidents" value={stats?.total_incidents ?? "—"} />
        <StatTile
          testId="stat-last-updated"
          label="Last updated"
          value={stats?.last_updated ? formatRelative(stats.last_updated) : "—"}
        />
        <StatTile
          testId="stat-categories"
          label="Categories"
          value={stats ? Object.keys(stats.by_category).length : "—"}
        />
        <StatTile
          testId="stat-states"
          label="States affected"
          value={stats ? stats.top_states.length : "—"}
        />
      </div>

      <div className="mb-6 grid grid-cols-2 gap-4">
        <TimelineChart data={stats?.timeline ?? []} />
        <SeverityBreakdown data={stats?.by_severity ?? {}} />
      </div>

      <TopStatesTable data={stats?.top_states ?? []} />
    </PageShell>
  );
}
