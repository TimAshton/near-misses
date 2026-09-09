import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { PageShell } from "../components/layout/PageShell";
import { fetchIncident } from "../lib/api";
import type { Incident } from "../lib/types";
import { formatDateTime, severityLabel } from "../lib/formatters";

export function IncidentDetail() {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rawOpen, setRawOpen] = useState(false);

  useEffect(() => {
    if (!id) return;
    fetchIncident(id)
      .then(setIncident)
      .catch((err: Error) => setError(err.message));
  }, [id]);

  if (error) {
    return (
      <PageShell title="Incident not found">
        <p className="text-red-400">{error}</p>
        <Link to="/reports" className="text-blue-400 hover:text-blue-300">
          Back to reports
        </Link>
      </PageShell>
    );
  }

  if (!incident) {
    return (
      <PageShell title="Loading…">
        <p className="text-gray-400">Loading incident…</p>
      </PageShell>
    );
  }

  return (
    <PageShell title={incident.title}>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-4">
          <dl
            data-testid="incident-fields"
            className="grid grid-cols-2 gap-x-6 gap-y-3 rounded-lg border border-gray-800 bg-gray-900 p-4 text-sm"
          >
            <Field label="Category" value={incident.category} />
            <Field label="Event type" value={incident.event_type} />
            <Field label="Severity" value={severityLabel(incident.severity)} />
            <Field label="Source" value={incident.source} />
            <Field label="Occurred" value={formatDateTime(incident.occurred_at)} />
            <Field label="Ingested" value={formatDateTime(incident.ingested_at)} />
            <Field label="Location" value={incident.location.display_name} />
            <Field
              label="Coordinates"
              value={`${incident.location.lat.toFixed(4)}, ${incident.location.lng.toFixed(4)}`}
            />
          </dl>

          <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
            <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-gray-500">
              Description
            </h2>
            <p className="text-sm text-gray-200">{incident.description}</p>
          </div>

          <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
            <button
              data-testid="raw-data-toggle"
              onClick={() => setRawOpen((v) => !v)}
              className="text-sm font-medium uppercase tracking-wide text-gray-500 hover:text-gray-300"
            >
              {rawOpen ? "▼" : "▶"} Raw source data
            </button>
            {rawOpen && (
              <pre
                data-testid="raw-data-content"
                className="mt-3 max-h-96 overflow-auto rounded bg-gray-950 p-3 text-xs text-gray-300"
              >
                {JSON.stringify(incident.raw, null, 2)}
              </pre>
            )}
          </div>

          <a
            href={incident.source_url}
            target="_blank"
            rel="noreferrer"
            className="inline-block text-sm font-medium text-blue-400 hover:text-blue-300"
          >
            View original source →
          </a>
        </div>

        <div className="col-span-1">
          <div
            data-testid="incident-pin-map"
            className="h-64 w-full rounded-lg border border-gray-800 bg-gray-900 p-4 text-sm text-gray-500"
          >
            Map pin: {incident.location.lat.toFixed(4)}, {incident.location.lng.toFixed(4)}
          </div>
        </div>
      </div>
    </PageShell>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-gray-500">{label}</dt>
      <dd className="text-gray-100">{value}</dd>
    </div>
  );
}
