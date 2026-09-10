# SPEC.md — US Incident Map

## Overview

A large-screen web application that overlays publicly available US incident data (aviation, seismic, weather, infrastructure) onto an interactive map. Data is polled from free public APIs, normalized to a shared schema, and stored in a persistent dataset on AWS. No authentication required.

---

## Goals

- Visualize real-world US incident data on an interactive map
- Poll live APIs on a scheduled interval and persist normalized data
- Support multiple incident categories (phased rollout)
- Provide map, dashboard, and reporting views
- Deploy fully on AWS via Terraform

---

## Phase 1 — Aviation (build and get approval before proceeding)

**Data Source:** FAA Accident & Incident Data System (AIDS) / Aviation Safety Hotline  
**API:** https://aviationweather.gov/api/data/ (free, no key)  
**Backup:** NTSB Aviation Accident Database  
**Poll interval:** Every 5 minutes (or manually triggered via UI refresh button)  
**Scope:** US only

**What to collect:**
- Incident ID
- Event type (accident, near-miss, runway incursion, etc.)
- Date and time (UTC)
- Location (lat/lng, airport code, city, state)
- Aircraft type
- Severity
- Description / narrative
- Source URL

---

## Phases 2–5 (pending Phase 1 approval)

| Phase | Category | Notes |
|---|---|---|
| 2 | Train incidents | Broken tracks, derailments, bridge closures — FRA API |
| 3 | Earthquakes | USGS Earthquake Hazards API |
| 4 | Tidal waves / Tsunamis | NOAA Tsunami Warning Center API |
| 5 | Hurricanes | NOAA National Hurricane Center API |
| 6 (added post-launch, not in original plan) | Wildfires | NIFC WFIGS current wildland fire incidents |

For incidents covering large land areas (hurricanes, seismic zones), place the icon at the geographic center of the affected region.

---

## Normalized Incident Schema

All data sources write to a shared schema regardless of type:

```json
{
  "id": "uuid",
  "source": "faa | ntsb | fra | usgs | noaa-tsunami | noaa-hurricane | nifc-wildfire",
  "category": "aviation | rail | seismic | tsunami | hurricane | wildfire",
  "event_type": "string",
  "severity": "low | medium | high | critical",
  "title": "string",
  "description": "string",
  "occurred_at": "ISO8601",
  "ingested_at": "ISO8601",
  "location": {
    "lat": "float",
    "lng": "float",
    "city": "string",
    "state": "string",
    "display_name": "string"
  },
  "source_url": "string",
  "raw": {}
}
```

`raw` stores the original API response for auditing and reprocessing.

---

## Tech Stack

### Frontend
- **React + TypeScript** (Vite)
- **MapLibre GL JS** (styled with [OpenFreeMap](https://openfreemap.org) tiles) — interactive map. Originally spec'd as Mapbox GL JS; switched during implementation to avoid requiring a Mapbox account/billing-profile signup for a free-tier key — MapLibre is Mapbox GL JS's open-source fork with the same API, and OpenFreeMap needs no signup, key, or usage cap.
- **Tailwind CSS** — styling
- **Recharts** — dashboard charts
- **WebSocket client** — receives real-time incident pushes, updates map and dashboard without page refresh
- Large screen only (min-width: 1024px), all modern browsers

### Backend
- **Python / FastAPI** — REST API + polling workers
- **APScheduler** or **Celery + Redis** — 5-minute polling jobs
- **WebSockets (FastAPI native)** — push new incidents to connected clients in real time
- **SQLAlchemy** — ORM

### Data
- **AWS RDS (PostgreSQL)** — normalized incident storage, used for both write and query
- **S3** — raw API response archive

### Infrastructure (Terraform)
- VPC, subnets, security groups
- ECS Fargate — API + worker containers
- RDS PostgreSQL
- S3 bucket
- CloudFront + S3 — frontend hosting
- ECR — container registry
- IAM roles

---

## Pages

### `/` — Home
- Brief description of the project
- Summary stats (total incidents, last updated, active categories)
- Quick-access links to Map and Dashboard

### `/map` — Map
- Full-screen interactive US map
- Incident icons by category (plane icon for aviation, etc.)
- Click icon → modal preview with link to detail page
- Filter panel: by category, severity, date range
- Icon placement: exact lat/lng for point incidents, geographic center for area events

### `/dashboard` — Dashboard
- Incident counts by category
- Timeline chart (incidents over time)
- Severity breakdown
- Top states by incident count
- Last 24h / 7d / 30d toggles
- Manual refresh button — triggers an immediate API poll and updates the UI when complete

### `/reports` — Reporting
- Tabular view of all incidents
- Sortable, filterable columns
- CSV export

### `/incidents/:id` — Incident Detail
- All normalized fields displayed
- Raw source data (collapsible)
- Map pin showing location
- Link back to source

### `/about` — About
- Project description
- Data sources and attribution
- Refresh cadence and data lag notes

---

## Data Pipeline

```
Scheduler (every 5 min) or POST /api/poll/trigger
  → Fetch from API
  → Validate response
  → Normalize to schema
  → Deduplicate (check existing ID or source+occurred_at)
  → Write to RDS
  → Archive raw response to S3
  → Broadcast new incidents to all connected clients via WebSocket
```

---

## Testing

- **Playwright** — E2E tests for all pages, map interaction, detail page navigation
- **Pytest** — unit tests for normalization functions, deduplication logic
- **Pytest + httpx** — API endpoint tests

---

## Terraform Outputs

```
frontend_url     = https://incidents.tashton.com (or similar)
api_url          = https://api.incidents.tashton.com
rds_endpoint     = (internal)
```

---

## Constraints

- US incidents only — filter at ingestion, reject non-US coordinates
- No user login or authentication
- Free APIs only — no paid data sources
- Phase 1 must be approved before Phase 2 begins
- All infrastructure defined in Terraform — no manual AWS console changes

---

## Out of Scope (v1)

- User accounts or saved searches
- Push notifications or alerts
- Mobile support
- Real-time WebSocket updates — included in v1
- Non-US incidents