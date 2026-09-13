import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";

// Idempotent — safe to call again alongside IncidentMap.tsx's own call (see
// its comment for why this is needed at all).
maplibregl.setWorkerUrl(maplibreWorkerUrl);

const MAP_STYLE = "https://tiles.openfreemap.org/styles/dark";

interface LocationPreviewMapProps {
  lat: number;
  lng: number;
  zoom?: number;
}

/** A small, non-interactive map centered on one incident — the closest
 * thing to "a photo of the location" this app can show inline without an
 * API key (real street-level imagery needs a billing-enabled Google/Mapbox
 * account; see lib/mapLinks.ts for keyless links out to Street View instead).
 */
export function LocationPreviewMap({ lat, lng, zoom = 11 }: LocationPreviewMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: [lng, lat],
      zoom,
      interactive: false,
    });
    new maplibregl.Marker({ color: "#ef4444" }).setLngLat([lng, lat]).addTo(map);

    return () => map.remove();
  }, [lat, lng, zoom]);

  return (
    <div
      ref={containerRef}
      data-testid="incident-location-preview-map"
      className="h-full w-full"
    />
  );
}
