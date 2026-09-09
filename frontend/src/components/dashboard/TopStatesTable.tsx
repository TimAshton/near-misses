import type { StateCount } from "../../lib/types";

interface TopStatesTableProps {
  data: StateCount[];
}

export function TopStatesTable({ data }: TopStatesTableProps) {
  return (
    <div
      data-testid="top-states-table"
      className="w-full rounded-lg border border-gray-800 bg-gray-900 p-4"
    >
      <p className="mb-2 text-sm font-medium text-gray-300">Top states</p>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs uppercase text-gray-500">
            <th className="pb-2">State</th>
            <th className="pb-2 text-right">Incidents</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.state} className="border-t border-gray-800">
              <td className="py-1.5 text-gray-200">{row.state}</td>
              <td className="py-1.5 text-right text-gray-200">{row.count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
