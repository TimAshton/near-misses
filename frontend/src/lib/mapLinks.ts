/** External map/imagery links built from a lat/lng — no API key needed for
 * any of these, so no signup/billing profile is required (same constraint
 * that drove picking MapLibre + OpenFreeMap for the main map — see
 * IncidentMap.tsx and _specs/SPEC.md).
 */

/** Opens Google Maps' Street View (Photosphere) layer at a point — the
 * classic keyless `cbll`/`layer=c` deep link. Google falls back to a plain
 * map view on its own if no Street View coverage exists there. */
export function streetViewUrl(lat: number, lng: number): string {
  return `https://www.google.com/maps?layer=c&cbll=${lat},${lng}`;
}

export function googleMapsUrl(lat: number, lng: number): string {
  return `https://www.google.com/maps?q=${lat},${lng}`;
}
