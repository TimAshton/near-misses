# NOAA National Hurricane Center — Phase 5 (hurricane)

**Endpoint**: `GET https://www.nhc.noaa.gov/CurrentStorms.json`

Public, unauthenticated, real-time JSON — no key. Lists every storm NHC is
currently tracking across the Atlantic and Eastern Pacific basins (`id`,
`name`, `classification`, `intensity` in knots, `pressure`, a direct
`latitudeNumeric`/`longitudeNumeric` current position, `lastUpdate`, and a
link to the public advisory text). Unlike NTSB/FRA there's no reporting lag —
this is the storm's live current state — and unlike USGS/NWS there's no
"most recent N" feed shape to worry about, since it's just whatever NHC is
tracking right now (often zero storms outside hurricane season).

**Scope note**: like every other source, only a storm whose *current*
position falls in the US bounding boxes (`ingestion/us_bounds.py`) is kept.
A storm still far out at sea but forecast to threaten the US coast won't
show up until its tracked position actually enters US waters — this app
doesn't attempt forecast-track-based inclusion, matching how every other
source here works off current/reported position, not prediction.

**Severity** is derived from `intensity` (sustained wind speed, knots →
mph) against the standard Saffir-Simpson thresholds, not from
`classification` directly — a "TS" storm about to be upgraded and a fresh
"HU" are both meaningfully different from a Category 3+, so wind speed is
the more useful signal.

**Dedup note**: `id` (NHC's ATCF storm identifier, e.g. `ep142026`) is
stable for a storm's entire lifetime, unlike tsunami alerts which reissue a
new id per update. This means a storm is recorded once, at first detection
— later polls see the same `id` and dedupe, so this map doesn't track a
storm's intensifying/weakening over time, only that it existed. That's a
limitation of the whole pipeline (nothing here updates an existing row), not
specific to hurricanes.
