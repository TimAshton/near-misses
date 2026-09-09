interface StatTileProps {
  label: string;
  value: string | number;
  testId?: string;
}

export function StatTile({ label, value, testId }: StatTileProps) {
  return (
    <div
      data-testid={testId}
      className="rounded-lg border border-gray-800 bg-gray-900 p-4"
    >
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-gray-100">{value}</p>
    </div>
  );
}
