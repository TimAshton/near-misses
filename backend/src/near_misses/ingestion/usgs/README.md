# USGS Earthquake Hazards Program — Phase 3 (seismic)

**Endpoint**: `GET https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson`

Public, unauthenticated, real-time GeoJSON feed — no key, no reverse-engineering
required (unlike `../ntsb`). USGS publishes several pre-built feeds combining a
time window (hour/day/week/month) with a minimum magnitude (all/1.0/2.5/4.5/
significant); `all_hour` is used here since it lines up with the shared 5-minute
poll interval while still catching low-magnitude events. Events already seen are
skipped by the normal source+occurred_at+lat/lng dedupe, so overlap between polls
is harmless.

Each `features[]` entry is one earthquake:
- `id` — stable USGS event id, used as `source_id`
- `properties.mag` — magnitude, mapped to our severity scale
- `properties.place`, `properties.title` — human-readable location/summary
- `properties.time` — event time, epoch milliseconds UTC
- `properties.url` — link to the USGS event page
- `geometry.coordinates` — `[lng, lat, depth_km]`

Global feed: non-US events (e.g. Indonesia, Japan) are filtered out downstream
by `ingestion/us_bounds.py`, same as every other source.
