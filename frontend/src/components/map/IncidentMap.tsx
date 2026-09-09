import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { Incident } from "../../lib/types";
import { createMarkerElement } from "./IncidentMarker";

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN as string | undefined;

// Center of the continental US.
const US_CENTER: [number, number] = [-98.5795, 39.8283];
const US_DEFAULT_ZOOM = 3.4;

interface IncidentMapProps {
  incidents: Incident[];
  onSelect: (incident: Incident) => void;
}

export function IncidentMap({ incidents, onSelect }: IncidentMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!MAPBOX_TOKEN || !containerRef.current) return;
    mapboxgl.accessToken = MAPBOX_TOKEN;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: US_CENTER,
      zoom: US_DEFAULT_ZOOM,
    });
    map.addControl(new mapboxgl.NavigationControl(), "top-right");
    map.on("load", () => setMapReady(true));
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !mapReady) return;

    for (const marker of markersRef.current) marker.remove();
    markersRef.current = [];

    for (const incident of incidents) {
      const el = createMarkerElement({ incident, onClick: () => onSelect(incident) });
      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([incident.location.lng, incident.location.lat])
        .addTo(mapRef.current);
      markersRef.current.push(marker);
    }
  }, [incidents, mapReady, onSelect]);

  if (!MAPBOX_TOKEN) {
    return (
      <div
        data-testid="mapbox-token-missing"
        className="flex h-full w-full flex-col items-center justify-center gap-2 border border-dashed border-gray-700 bg-gray-900 text-center text-gray-400"
      >
        <p className="text-lg font-medium text-gray-200">Map unavailable</p>
        <p className="max-w-sm text-sm">
          No Mapbox access token is configured. Set{" "}
          <code className="rounded bg-gray-800 px-1 py-0.5">VITE_MAPBOX_TOKEN</code> in your
          environment to enable the interactive map.
        </p>
      </div>
    );
  }

  return <div ref={containerRef} data-testid="incident-map" className="h-full w-full" />;
}
