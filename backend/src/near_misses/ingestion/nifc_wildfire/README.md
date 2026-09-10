# NIFC Wildland Fire Incident Locations — wildfire (not in original SPEC.md phases)

**Endpoint**: `GET https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Incident_Locations_Current/FeatureServer/0/query`

Public, unauthenticated, real-time ArcGIS Feature Service — no key. This is
NIFC's (National Interagency Fire Center) WFIGS (Wildland Fire Interagency
Geospatial Services) current-incidents layer, the same authoritative feed
that backs InciWeb and NIFC's own public dashboards. Each record is one
active/recent wildfire: `IncidentName`, `IncidentSize` (acres, often null for
a just-discovered fire), `PercentContained`, `FireDiscoveryDateTime` (epoch
ms), `POOState`/`POOCounty` (point of origin), `FireCause`, direct point
geometry (`x`/`y` = lng/lat), and a stable `UniqueFireIdentifier`.

Queried with `IncidentTypeCategory='WF'` to keep only actual wildfires —
the same layer also carries prescribed burns (`RX`) and other planned-fire
categories that aren't incidents in the sense this map cares about.

**No source_url**: unlike other sources, WFIGS doesn't carry a direct
per-fire public webpage in this feed (InciWeb pages exist for some large
fires but aren't reliably linkable from a stable field here), so
`source_url` is left null rather than guessing at a URL.

**Severity** is derived from `IncidentSize` (acres) since WFIGS has no
severity field of its own: ≥10,000 acres → critical, ≥1,000 → high, ≥100 →
medium, else (including a freshly-discovered fire with no size yet) → low.
