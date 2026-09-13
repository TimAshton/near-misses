import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TimelinePoint } from "../../lib/types";
import { formatDateTime } from "../../lib/formatters";

interface WildfireTrendPanelProps {
  data: TimelinePoint[];
}

type Direction = "up" | "down" | "flat";

// Below this, day-to-day noise isn't a real trend worth calling out.
const FLAT_THRESHOLD_PCT = 10;

function trendDirection(data: TimelinePoint[]): { direction: Direction; percentChange: number } {
  if (data.length < 2) return { direction: "flat", percentChange: 0 };

  const mid = Math.floor(data.length / 2);
  const earlier = data.slice(0, mid).reduce((sum, p) => sum + p.count, 0);
  const recent = data.slice(mid).reduce((sum, p) => sum + p.count, 0);

  if (earlier === 0) {
    return { direction: recent > 0 ? "up" : "flat", percentChange: recent > 0 ? 100 : 0 };
  }

  const percentChange = ((recent - earlier) / earlier) * 100;
  if (Math.abs(percentChange) < FLAT_THRESHOLD_PCT) return { direction: "flat", percentChange };
  return { direction: percentChange > 0 ? "up" : "down", percentChange };
}

// More new fires is the bad direction here, so "up" reads as a warning
// color and "down" as reassuring — not the generic up=green/down=red a
// growth metric would use. Reuses this app's existing severity colors
// (SEVERITY_COLOR.critical / .low in lib/formatters.ts) rather than
// introducing a new pair for the same good/bad meaning.
const DIRECTION_STYLE: Record<Direction, { color: string; icon: string; label: string }> = {
  up: { color: "#ef4444", icon: "▲", label: "Upswing" },
  down: { color: "#22c55e", icon: "▼", label: "Downswing" },
  flat: { color: "#9ca3af", icon: "→", label: "Steady" },
};

export function WildfireTrendPanel({ data }: WildfireTrendPanelProps) {
  const { direction, percentChange } = trendDirection(data);
  const style = DIRECTION_STYLE[direction];

  return (
    <div
      data-testid="wildfire-trend-panel"
      className="h-64 w-full rounded-lg border border-gray-800 bg-gray-900 p-4"
    >
      <div className="mb-2 flex items-center justify-between">
        <p className="text-sm font-medium text-gray-300">New wildfires, last 90 days</p>
        <p
          data-testid="wildfire-trend-direction"
          className="flex items-center gap-1 text-sm font-semibold"
          style={{ color: style.color }}
        >
          <span aria-hidden="true">{style.icon}</span>
          {style.label}
          {data.length >= 2 && (
            <span className="font-normal text-gray-500">
              ({percentChange > 0 ? "+" : ""}
              {percentChange.toFixed(0)}%, first half vs. second half)
            </span>
          )}
        </p>
      </div>
      <ResponsiveContainer width="100%" height="80%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="bucket"
            stroke="#6b7280"
            fontSize={11}
            tickFormatter={(v: string) => new Date(v).toLocaleDateString()}
          />
          <YAxis stroke="#6b7280" fontSize={11} allowDecimals={false} />
          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #1f2937", color: "#e5e7eb" }}
            labelFormatter={(v) => (typeof v === "string" ? formatDateTime(v) : String(v))}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke={style.color}
            fill={style.color}
            fillOpacity={0.15}
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
