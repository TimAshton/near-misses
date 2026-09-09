import { Link } from "react-router-dom";
import type { Incident, IncidentFilters } from "../../lib/types";
import { formatDateTime, severityLabel } from "../../lib/formatters";

interface IncidentTableProps {
  incidents: Incident[];
  filters: IncidentFilters;
  onSortChange: (sort: string, order: "asc" | "desc") => void;
}

const COLUMNS: { key: string; label: string }[] = [
  { key: "occurred_at", label: "Occurred" },
  { key: "category", label: "Category" },
  { key: "severity", label: "Severity" },
  { key: "title", label: "Title" },
  { key: "location.state", label: "State" },
];

export function IncidentTable({ incidents, filters, onSortChange }: IncidentTableProps) {
  function handleHeaderClick(key: string) {
    const nextOrder = filters.sort === key && filters.order === "asc" ? "desc" : "asc";
    onSortChange(key, nextOrder);
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-800">
      <table className="w-full text-sm" data-testid="incident-table">
        <thead className="bg-gray-900">
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                onClick={() => handleHeaderClick(col.key)}
                className="cursor-pointer px-3 py-2 text-left text-xs font-medium uppercase text-gray-400 hover:text-gray-100"
              >
                {col.label}
                {filters.sort === col.key ? (filters.order === "asc" ? " ▲" : " ▼") : ""}
              </th>
            ))}
            <th className="px-3 py-2" />
          </tr>
        </thead>
        <tbody>
          {incidents.map((incident) => (
            <tr key={incident.id} className="border-t border-gray-800 hover:bg-gray-900/60" data-testid="incident-row">
              <td className="px-3 py-2 text-gray-300">{formatDateTime(incident.occurred_at)}</td>
              <td className="px-3 py-2 text-gray-300">{incident.category}</td>
              <td className="px-3 py-2 text-gray-300">{severityLabel(incident.severity)}</td>
              <td className="px-3 py-2 text-gray-100">{incident.title}</td>
              <td className="px-3 py-2 text-gray-300">{incident.location.state ?? "—"}</td>
              <td className="px-3 py-2">
                <Link to={`/incidents/${incident.id}`} className="text-blue-400 hover:text-blue-300">
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
