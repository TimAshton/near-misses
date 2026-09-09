import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TimelinePoint } from "../../lib/types";
import { formatDateTime } from "../../lib/formatters";

interface TimelineChartProps {
  data: TimelinePoint[];
}

export function TimelineChart({ data }: TimelineChartProps) {
  return (
    <div data-testid="timeline-chart" className="h-64 w-full rounded-lg border border-gray-800 bg-gray-900 p-4">
      <p className="mb-2 text-sm font-medium text-gray-300">Incidents over time</p>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data}>
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
          <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
