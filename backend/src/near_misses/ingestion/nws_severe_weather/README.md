# NOAA/NWS Severe Weather Alerts — severe_weather (not in original SPEC.md phases)

**Endpoint**: `GET https://api.weather.gov/alerts/active?severity=Extreme`

Same public, unauthenticated, real-time CAP-derived API as nws_tsunami (see
its README for the general shape of an alert and the geometry/zone-centroid
resolution both sources share via `ingestion/nws_alerts.py`). The difference
here is the filter: `severity=Extreme` rather than a fixed `event` list —
per the explicit ask that started this ("extreme and severe and dangerous
weather... only add the most severe"), this tracks whatever event type NWS
is currently calling Extreme (Tornado Emergency, Extreme Wind Warning, a
major Hurricane Warning, etc.) rather than a hand-picked list of event
names, so a genuinely life-threatening alert type that isn't anticipated
here still gets picked up.

**Tsunami alerts are excluded** (`client.py`'s `_EXCLUDED_EVENTS`) even
though some reach Extreme severity — those are already tracked as their own
category by `nws_tsunami`, and without this exclusion the same underlying
alert would appear twice on the map under two different categories/icons.

**No dedicated severity policy**: `severity_policy.py` still requires
critical (matching wildfire), but the `severity=Extreme` filter already
means almost every fetched record maps to critical anyway — the policy
entry is a backstop, not the primary filter, in case a record is ever
missing its `severity` field.

**Overlap with the hurricane category is accepted, not filtered.** NWS may
issue an Extreme-severity Hurricane/Storm Surge Warning for a coastal zone
for the same storm nhc_hurricane is already tracking by center position —
these are different signals (a zone under warning vs. the storm's current
position) from different sources, so both showing up is treated as useful
rather than duplicate.
