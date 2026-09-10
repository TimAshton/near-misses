# NOAA/NWS Tsunami Alerts — Phase 4 (tsunami)

**Endpoint**: `GET https://api.weather.gov/alerts/active?event=Tsunami%20Warning,Tsunami%20Watch,Tsunami%20Advisory`

Public, unauthenticated, real-time JSON (CAP-derived) API — no key. Requires a
descriptive `User-Agent` header per NWS API etiquette (`settings.nws_user_agent`);
requests without one are more likely to be rate-limited. This is the same API
NOAA's Tsunami Warning Centers (NTWC/PTWC) publish through — SPEC.md names "NOAA
Tsunami Warning Center API" generically, and `api.weather.gov` is NOAA/NWS's
public alerts distribution for it.

**Location is the tricky part.** Unlike USGS earthquakes (a lat/lng point per
event), NWS alerts cover a zone/coastline and almost always have
`geometry: null` — only `properties.areaDesc` (text) and
`properties.geocode.UGC` (zone codes) describe where. Per SPEC.md ("place the
icon at the geographic center of the affected region" for area-based
incidents), `client.py` resolves this itself: for each alert with no geometry,
it fetches `https://api.weather.gov/zones/forecast/{UGC}` for the first
affected zone (that endpoint always has a real Polygon) and stashes a computed
centroid on the raw record as `_resolved_centroid`, cached per zone within one
poll so alerts sharing a zone don't refetch it. `normalizer.py` uses the
alert's own geometry when present, falling back to `_resolved_centroid`.

Each `features[]` entry's `properties.id` (a stable CAP identifier) is used as
`source_id` — note NWS reissues an updated alert as a *new* id as it evolves
(watch → warning, or a routine update), so the same real-world event can
appear as more than one incident row over its lifetime, same as any
other source tracking an evolving situation.
