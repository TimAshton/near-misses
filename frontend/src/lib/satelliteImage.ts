import { isoDateDaysAgo } from "./formatters";

/** Builds a keyless satellite-image URL for a storm via NASA's GIBS
 * Worldview Snapshot API — no signup/API key required, the same constraint
 * that ruled out Google/Mapbox satellite tiles elsewhere (see mapLinks.ts).
 * Renders a GOES-East true-color capture cropped to a box around the
 * storm's reported center.
 */
const SNAPSHOT_URL = "https://wvs.earthdata.nasa.gov/api/v1/snapshot";
const BOX_DEGREES = 6;

/** GIBS only has same-day imagery once it's finished processing, so "recent"
 * clamps to yesterday; older incidents use their own occurred_at date since
 * that's the capture that actually shows the storm. */
function satelliteDateFor(occurredAt: string): string {
  const occurred = occurredAt.slice(0, 10);
  const yesterday = isoDateDaysAgo(1);
  return occurred < yesterday ? occurred : yesterday;
}

export function stormSatelliteImageUrl(lat: number, lng: number, occurredAt: string): string {
  const south = Math.max(lat - BOX_DEGREES, -90);
  const north = Math.min(lat + BOX_DEGREES, 90);
  const west = Math.max(lng - BOX_DEGREES, -180);
  const east = Math.min(lng + BOX_DEGREES, 180);

  const params = new URLSearchParams({
    REQUEST: "GetSnapshot",
    LAYERS: "GOES-East_ABI_GeoColor",
    CRS: "EPSG:4326",
    TIME: satelliteDateFor(occurredAt),
    BBOX: `${south},${west},${north},${east}`,
    FORMAT: "image/jpeg",
    WIDTH: "640",
    HEIGHT: "640",
  });
  return `${SNAPSHOT_URL}?${params.toString()}`;
}
