import { SEVERITY_COLOR } from "../../lib/formatters";
import type { Incident } from "../../lib/types";

const CATEGORY_GLYPH: Record<string, string> = {
  aviation: "✈",
  rail: "🚆",
  seismic: "⛰",
  tsunami: "🌊",
  hurricane: "🌀",
};

interface IncidentMarkerElementProps {
  incident: Incident;
  onClick: () => void;
}

/** Builds a plain DOM node for use as a Mapbox GL marker element. */
export function createMarkerElement({ incident, onClick }: IncidentMarkerElementProps): HTMLDivElement {
  const el = document.createElement("div");
  el.setAttribute("data-testid", "incident-marker");
  el.setAttribute("data-incident-id", incident.id);
  el.style.width = "28px";
  el.style.height = "28px";
  el.style.borderRadius = "50%";
  el.style.display = "flex";
  el.style.alignItems = "center";
  el.style.justifyContent = "center";
  el.style.fontSize = "14px";
  el.style.cursor = "pointer";
  el.style.border = "2px solid white";
  el.style.backgroundColor = SEVERITY_COLOR[incident.severity];
  el.style.boxShadow = "0 1px 4px rgba(0,0,0,0.5)";
  el.textContent = CATEGORY_GLYPH[incident.category] ?? "•";
  el.title = incident.title;
  el.addEventListener("click", (e) => {
    e.stopPropagation();
    onClick();
  });
  return el;
}
