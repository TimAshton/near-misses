import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Severity } from "../../lib/types";
import { SEVERITY_COLOR, severityLabel } from "../../lib/formatters";

interface SeverityBreakdownProps {
  data: Record<string, number>;
}

export function SeverityBreakdown({ data }: SeverityBreakdownProps) {
  const entries = Object.entries(data).map(([severity, count]) => ({
    severity: severity as Severity,
    name: severityLabel(severity as Severity),
    value: count,
  }));

  return (
    <div
      data-testid="severity-breakdown"
      className="h-64 w-full rounded-lg border border-gray-800 bg-gray-900 p-4"
    >
      <p className="mb-2 text-sm font-medium text-gray-300">Severity breakdown</p>
      <ResponsiveContainer width="100%" height="85%">
        <PieChart>
          <Pie data={entries} dataKey="value" nameKey="name" innerRadius={40} outerRadius={70}>
            {entries.map((entry) => (
              <Cell key={entry.severity} fill={SEVERITY_COLOR[entry.severity]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: "#111827", border: "1px solid #1f2937", color: "#e5e7eb" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
