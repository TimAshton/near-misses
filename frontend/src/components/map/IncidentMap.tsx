import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Incident } from "../../lib/types";
import { createMarkerElement } from "./IncidentMarker";

// OpenFreeMap: no signup, no API key, no usage cap — https://openfreemap.org
const MAP_STYLE = "https://tiles.openfreemap.org/styles/dark";

// Center of the continental US.
const US_CENTER: [number, number] = [-98.5795, 39.8283];
const US_DEFAULT_ZOOM = 3.4;

interface IncidentMapProps {
  incidents: Incident[];
  onSelect: (incident: Incident) => void;
}

export function IncidentMap({ incidents, onSelect }: IncidentMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [mapReady, setMapReady] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: US_CENTER,
      zoom: US_DEFAULT_ZOOM,
    });
    map.addControl(new maplibregl.NavigationControl(), "top-right");
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
      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([incident.location.lng, incident.location.lat])
        .addTo(mapRef.current);
      markersRef.current.push(marker);
    }
  }, [incidents, mapReady, onSelect]);

  return <div ref={containerRef} data-testid="incident-map" className="h-full w-full" />;
}
