import { isoDateDaysAgo } from "./formatters";

/** Builds keyless satellite-image URLs for a storm via NASA's GIBS
 * Worldview Snapshot API — no signup/API key required, the same constraint
 * that ruled out Google/Mapbox satellite tiles elsewhere (see mapLinks.ts).
 *
 * Uses VIIRS true-color rather than GOES-East GeoColor: GOES-East's
 * near-real-time layer only keeps ~1 day of imagery in GIBS, so anything
 * older returns a "no data" response — which is still a valid, solid-black
 * JPEG rather than an HTTP error, so an <img> tag alone can't detect it.
 * VIIRS has a deep daily archive (back to ~2012), so it works for old
 * storms too; candidateSatelliteDates() below still has the caller check
 * each try's `Data-Present` response header rather than trusting the image,
 * since even VIIRS occasionally has a one-day gap.
 */
const SNAPSHOT_URL = "https://wvs.earthdata.nasa.gov/api/v1/snapshot";
const LAYER = "VIIRS_SNPP_CorrectedReflectance_TrueColor";
const BOX_DEGREES = 6;

function isoDateMinusOne(iso: string): string {
  const date = new Date(`${iso}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() - 1);
  return date.toISOString().slice(0, 10);
}

export function stormSatelliteImageUrl(lat: number, lng: number, date: string): string {
  const south = Math.max(lat - BOX_DEGREES, -90);
  const north = Math.min(lat + BOX_DEGREES, 90);
  const west = Math.max(lng - BOX_DEGREES, -180);
  const east = Math.min(lng + BOX_DEGREES, 180);

  const params = new URLSearchParams({
    REQUEST: "GetSnapshot",
    LAYERS: LAYER,
    CRS: "EPSG:4326",
    TIME: date,
    BBOX: `${south},${west},${north},${east}`,
    FORMAT: "image/jpeg",
    WIDTH: "640",
    HEIGHT: "640",
  });
  return `${SNAPSHOT_URL}?${params.toString()}`;
}

/** Capture dates to try, nearest-to-storm first: the storm's own date (or
 * today if that's in the future), then two days further back — covers
 * same-day imagery that hasn't finished processing yet, and the occasional
 * one-day gap in the archive. */
export function candidateSatelliteDates(occurredAt: string): string[] {
  const today = isoDateDaysAgo(0);
  const occurredDate = occurredAt.slice(0, 10);
  let date = occurredDate > today ? today : occurredDate;
  const dates = [date];
  for (let i = 0; i < 2; i++) {
    date = isoDateMinusOne(date);
    dates.push(date);
  }
  return dates;
}
