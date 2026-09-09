import { Link } from "react-router-dom";
import type { Incident } from "../../lib/types";
import { formatDateTime, severityLabel } from "../../lib/formatters";

interface IncidentPreviewModalProps {
  incident: Incident;
  onClose: () => void;
}

export function IncidentPreviewModal({ incident, onClose }: IncidentPreviewModalProps) {
  return (
    <div
      className="absolute inset-0 z-20 flex items-center justify-center bg-black/50"
      onClick={onClose}
      data-testid="incident-preview-backdrop"
    >
      <div
        className="w-96 rounded-lg border border-gray-800 bg-gray-900 p-5 shadow-xl"
        onClick={(e) => e.stopPropagation()}
        data-testid="incident-preview-modal"
      >
        <div className="mb-2 flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold text-gray-100">{incident.title}</h3>
          <button
            onClick={onClose}
            aria-label="Close"
            className="text-gray-400 hover:text-gray-100"
          >
            ✕
          </button>
        </div>
        <p className="mb-1 text-xs uppercase tracking-wide text-gray-500">
          {incident.category} · {severityLabel(incident.severity)}
        </p>
        <p className="mb-3 text-sm text-gray-300">{formatDateTime(incident.occurred_at)}</p>
        <p className="mb-4 line-clamp-4 text-sm text-gray-300">{incident.description}</p>
        <Link
          to={`/incidents/${incident.id}`}
          className="text-sm font-medium text-blue-400 hover:text-blue-300"
          data-testid="incident-preview-detail-link"
        >
          View full details →
        </Link>
      </div>
    </div>
  );
}
