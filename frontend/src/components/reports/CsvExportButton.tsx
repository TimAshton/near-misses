import type { IncidentFilters } from "../../lib/types";
import { exportCsvUrl } from "../../lib/api";

interface CsvExportButtonProps {
  filters: IncidentFilters;
}

export function CsvExportButton({ filters }: CsvExportButtonProps) {
  return (
    <a
      href={exportCsvUrl(filters)}
      data-testid="csv-export-button"
      className="rounded-md border border-gray-700 px-4 py-2 text-sm font-medium text-gray-200 hover:bg-gray-800"
    >
      Export CSV
    </a>
  );
}
