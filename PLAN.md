# Technical Plan: US Incident Map — Phase 1 (Aviation) + Foundational Architecture

## Context

This repo currently has no application code — only `README.md`, `CLAUDE.md`, and `_specs/SPEC.md`. The spec describes a 5-phase, multi-category incident map, but explicitly gates all phases after Phase 1 on approval. This plan turns the spec into something buildable: it defines the shared foundation (schema, pipeline shape, repo layout, infra skeleton) that every phase will reuse, and gives a fully concrete, sequenced build plan for **Phase 1 (Aviation) only**. Phases 2–5 get a one-paragraph "extension pattern" note — no speculative design work is done for them, per the spec's own gating rule.

Two ambiguities in the spec were resolved with the project owner before finalizing this plan:
- **Data source**: the spec names `aviationweather.gov` as the Phase 1 API, but that service only serves current aviation *weather* (METAR/TAF/PIREP/AIRMET) — it has no accident/incident records. The spec's literal primary source, "FAA Accident & Incident Data System (AIDS) / Aviation Safety Hotline," is not a well-documented open public API. Decision: **spend a time-boxed spike investigating real access to FAA AIDS first** (Step 3 below), falling back to NTSB's public accident API (`data.ntsb.gov` / CAROL) if AIDS access isn't practically obtainable, since NTSB is the spec's own named "Backup."
- **WebSocket scope**: the spec both requires real-time WebSocket push (frontend bullet, pipeline diagram) and lists it under "Out of Scope (v1)" with a contradictory note. Decision: **WebSocket push is in scope for Phase 1**, since it's load-bearing throughout the pipeline and UI design.

---

## Repository Structure (monorepo)

```
near-misses/
  _specs/SPEC.md
  PLAN.md
  CLAUDE.md
  README.md
  docker-compose.yml              # local Postgres, localstack (S3), backend, frontend
  .github/workflows/ci.yml        # lint/test frontend + backend on PR
  frontend/
    package.json / vite.config.ts / tailwind.config.ts / tsconfig.json / index.html
    src/
      main.tsx, App.tsx
      routes/            Home.tsx, MapPage.tsx, Dashboard.tsx, Reports.tsx, IncidentDetail.tsx, About.tsx
      components/
        map/             IncidentMap.tsx, IncidentMarker.tsx, FilterPanel.tsx, IncidentPreviewModal.tsx
        dashboard/        StatTile.tsx, TimelineChart.tsx, SeverityBreakdown.tsx, TopStatesTable.tsx, RefreshButton.tsx
        reports/          IncidentTable.tsx, CsvExportButton.tsx
        layout/           NavBar.tsx, PageShell.tsx
      lib/               api.ts, ws.ts, types.ts, formatters.ts
      hooks/             useIncidents.ts, useWebSocketIncidents.ts
      styles/index.css
    tests/e2e/           home.spec.ts, map.spec.ts, dashboard.spec.ts, reports.spec.ts, incident-detail.spec.ts
    tests/playwright.config.ts
  backend/
    pyproject.toml, alembic.ini
    src/near_misses/
      main.py             # FastAPI app factory, router mounting, WS endpoint
      config.py           # env-based settings (pydantic-settings)
      db.py                # SQLAlchemy engine/session
      models/incident.py   # SQLAlchemy Incident model
      schemas/incident.py  # Pydantic schemas, matches SPEC schema
      api/routes/          incidents.py, stats.py, poll.py
      api/deps.py
      ws/manager.py        # ConnectionManager: register/broadcast
      ingestion/
        base.py             # SourceClient/Normalizer protocol shared by all phases
        faa_aids/           # client.py, normalizer.py — primary target, pending spike (Step 3)
        ntsb/               # client.py, normalizer.py — fallback source
        aviationweather/    # client.py — optional supplementary weather context
        dedup.py            # shared dedup logic (id or source+occurred_at)
        pipeline.py         # fetch -> validate -> normalize -> dedup -> persist -> archive -> broadcast
        us_bounds.py        # reject non-US coordinates
      storage/s3_archive.py # raw response archive (boto3, S3 or localstack endpoint)
      scheduler/jobs.py     # APScheduler job def, 5-min poll
    alembic/versions/
    tests/
      unit/       test_normalizer_*.py, test_dedup.py, test_us_bounds.py
      api/        test_incidents_endpoint.py, test_stats_endpoint.py, test_poll_trigger.py
      conftest.py # test DB fixture, httpx AsyncClient
  infra/terraform/
    environments/dev/     main.tf, variables.tf, outputs.tf, backend.tf
    modules/               network/, rds/, ecs/, ecr/, s3-archive/, frontend-hosting/, iam/
```

**Rationale**: `backend/src/near_misses/ingestion/<source>/` isolates each source's client + normalizer behind a shared `base.py` protocol, so Phase 2–5 sources (FRA, USGS, NOAA) slot in as siblings without touching pipeline, dedup, API, or frontend code.

---

## Shared Foundation (build once, reuse across all phases)

1. **Normalized incident schema** — implement exactly per SPEC.md, as both a SQLAlchemy model (`models/incident.py`: `id` UUID pk, `source`, `category`, `event_type`, `severity`, `title`, `description`, `occurred_at`/`ingested_at` timestamptz, `lat`/`lng`/`city`/`state`/`display_name`, `source_url`, `raw` JSONB) and a matching Pydantic schema with `category`/`severity` enums. Index `occurred_at`, `category`, `state`; add a unique constraint for dedup (on stable source ID where available, else composite `(source, occurred_at, lat, lng)`).

2. **Pipeline shape** (`ingestion/pipeline.py`) — one function, `run_ingestion(source_client, normalizer)`, identical for every source: fetch → validate (schema + `us_bounds`) → normalize → dedup (`dedup.py`) → persist → archive raw response to S3 → broadcast new incidents via `ws/manager.py`. Both the APScheduler job (every 5 min) and `POST /api/poll/trigger` call this exact same function so scheduled and manual runs can't drift.

3. **US-bounds filter** (`ingestion/us_bounds.py`) — bounding-box check (continental US + AK/HI); incidents outside are logged and dropped before persistence, not stored with a "rejected" flag.

4. **Infra skeleton (Terraform)** — build `infra/terraform/modules/*` once, sized for Phase 1 traffic. Phases 2–5 reuse the same DB, S3 bucket, and ECS services — no infra changes needed for later phases, just new ingestion code deployed in the same containers.

5. **Extension pattern for Phases 2–5** (brief note only, no further design) — each future phase adds one `ingestion/<source>/{client,normalizer}.py` pair, one scheduler job entry, and category-specific icon/legend entries in the frontend. Do not design these further until Phase 1 is approved.

---

## Phase 1 (Aviation) — Concrete Build Sequence

1. **Repo scaffold** — `frontend/`: `npm create vite@latest -- --template react-ts` + Tailwind, Mapbox GL JS, Recharts, React Router. `backend/`: `pyproject.toml` with FastAPI, SQLAlchemy, Alembic, APScheduler, boto3, pydantic-settings, httpx (uv or poetry for env management). `docker-compose.yml`: `postgres:16`, `localstack` (S3 only), `backend` (uvicorn --reload), optional `frontend` service. Root `.env.example` documenting `DATABASE_URL`, `S3_BUCKET`, `S3_ENDPOINT_URL`, `MAPBOX_TOKEN`, and source API base URLs.

2. **Schema + DB migrations** — `Incident` SQLAlchemy model + Alembic initial migration with indexes/unique constraint per Shared Foundation #1; verify against docker-compose Postgres.

3. **Data-source spike: FAA AIDS access** — before writing the primary ingestion client, time-box an investigation into whether FAA AIDS / Aviation Safety Hotline data is practically accessible as a public API or structured feed (documented endpoint, bulk data download, or otherwise). Document the outcome (endpoint, auth requirements, format, update cadence, any access restrictions) directly in `backend/src/near_misses/ingestion/faa_aids/README.md` or equivalent code comments. If AIDS proves inaccessible or unsuitable within the time-box, fall back to `ingestion/ntsb/` (NTSB CAROL API, `data.ntsb.gov`) as the working Phase 1 source — this fallback path should be scaffolded in parallel so the rest of the build isn't blocked on the spike's outcome.

4. **Ingestion, normalization, dedup** — `ingestion/<source>/client.py` (fetch, handle pagination), `ingestion/<source>/normalizer.py` (map raw record → normalized schema; document any non-obvious field mapping, e.g. severity heuristics, directly where the mapping happens). `ingestion/dedup.py`: query by stable source ID first, fall back to `(source, occurred_at, lat, lng)` proximity match. Unit tests (`tests/unit/test_normalizer_*.py`, `test_dedup.py`) using a captured fixture JSON response stored under `backend/tests/fixtures/`.

5. **REST API** — `GET /api/incidents` (filter by category/severity/state/date range, paginated), `GET /api/incidents/{id}` (full record incl. `raw`), `GET /api/stats` (counts by category/severity/state, timeline buckets, `last_updated`), `POST /api/poll/trigger` (runs `run_ingestion`, returns new-incident count). API tests via `httpx.AsyncClient` against a test Postgres.

6. **Scheduler** — APScheduler `BackgroundScheduler` in FastAPI lifespan, 5-minute job calling `run_ingestion`; confirm it shares the exact code path with `/api/poll/trigger`. Use in-process APScheduler rather than Celery+Redis for this single low-frequency job — simpler infra, no Redis dependency; revisit only if later phases need multi-worker fan-out.

7. **WebSocket broadcast** — `ws/manager.py` `ConnectionManager` (register/broadcast/disconnect), `/ws` endpoint in `main.py`. Pipeline calls `manager.broadcast()` after each new (non-duplicate) incident is persisted, so map and dashboard update live.

8. **Frontend: Map (`/map`)** — `IncidentMap.tsx` (Mapbox GL JS, US-centered, category icons), `useIncidents` (initial REST fetch), `useWebSocketIncidents` (live append via `/ws`), `FilterPanel.tsx` (category/severity/date, refetch on change), `IncidentPreviewModal.tsx` (marker click → summary + link to detail page).

9. **Frontend: Dashboard (`/dashboard`)** — `StatTile`, `TimelineChart` (Recharts via `/api/stats`), `SeverityBreakdown`, `TopStatesTable`; 24h/7d/30d toggle re-queries `/api/stats`; `RefreshButton` calls `POST /api/poll/trigger` and reflects new data via WS push.

10. **Frontend: Reports (`/reports`)** — `IncidentTable.tsx` with server-side sort/filter (reusing `/api/incidents` query params from Step 5); `CsvExportButton.tsx` backed by a server-side `GET /api/incidents/export.csv` endpoint honoring the same filters, to avoid partial/paginated exports.

11. **Frontend: Incident Detail (`/incidents/:id`)** — full normalized fields, collapsible `raw` JSON viewer, small Mapbox pin map, link to `source_url`.

12. **Home (`/`) and About (`/about`)** — Home: summary stats from `/api/stats`, links to Map/Dashboard. About: static content — data source attribution (FAA AIDS or NTSB, whichever Step 3 resolves to), refresh cadence (5 min), and an explicit note on data lag (investigation-driven sources like NTSB publish with delay after real-world events — disclose this rather than implying near-real-time coverage).

13. **Terraform infra (dev environment)** — `modules/network`, `rds`, `ecr`, `ecs` (single ECS service running the FastAPI app with the in-process scheduler — avoids a second task definition for Phase 1), `s3-archive`, `frontend-hosting` (S3 + CloudFront), `iam`. `environments/dev/outputs.tf` producing `frontend_url`, `api_url`, `rds_endpoint` per spec. Terraform applied manually by a human for this phase (no automated deploy pipeline requested).

14. **CI** — `.github/workflows/ci.yml`: lint/typecheck frontend (`eslint`, `tsc --noEmit`), lint backend (`ruff`), `pytest` (unit + API tests against a service-container Postgres), Playwright E2E against a docker-compose-launched stack.

15. **E2E tests (Playwright)** — one spec per page: home stats load, map renders markers and opens modal on click → navigates to detail, dashboard range toggles and refresh trigger, reports table sort/filter/export, incident detail shows raw data. Run against a seeded test DB, not the live external API, for determinism.

---

## Local Development (before AWS/Terraform exist)

- `docker-compose.yml`: `postgres` (local RDS stand-in), `localstack` running only S3 (`s3_archive.py` reads `S3_ENDPOINT_URL`, defaulting to real AWS in prod, localstack in dev/test), `backend` (uvicorn `--reload`), optional `frontend` (or run `npm run dev` on host for faster HMR, `VITE_API_URL` → `http://localhost:8000`).
- `config.py` reads all AWS-shaped values from env vars so the same code runs unmodified against localstack locally and real AWS when deployed — no environment branching in application code.
- ~~Mapbox requires a real API token even locally~~ — resolved (see Open Question 3): the map runs on MapLibre GL JS + OpenFreeMap tiles, no token/account needed anywhere.
- Fresh-clone order: `docker compose up postgres localstack` → `alembic upgrade head` → `uvicorn near_misses.main:app --reload` → `npm run dev` in `frontend/`.
- `POST /api/poll/trigger` is the primary way to exercise ingestion locally without waiting on the 5-minute scheduler.

---

## Testing Approach

- **Pytest unit** (`backend/tests/unit/`): normalization (raw record → normalized schema, using a captured fixture) and dedup logic (same ID twice → rejected; different ID, same time/location → accepted or rejected per proximity threshold — both cases covered).
- **Pytest + httpx API** (`backend/tests/api/`): `test_incidents_endpoint.py` (filtering, pagination), `test_stats_endpoint.py` (aggregation correctness against seeded rows), `test_poll_trigger.py` (mocks the source client so tests don't hit the live API; asserts the pipeline runs end-to-end and broadcasts).
- **Playwright E2E** (`frontend/tests/e2e/`): per Step 15 above, against a seeded backend, not live external APIs.

---

## Open Questions / Risks

1. **FAA AIDS access is unverified** (Step 3 spike) — if it turns out not to be a usable open API/feed, the fallback to NTSB should be confirmed with the spec owner once the spike concludes, since it changes what "Phase 1 approval" is actually approving.
2. **Source data lag** — investigation-driven sources (NTSB, and likely FAA AIDS) may lag real-world events by weeks/months; this should be disclosed on the About page rather than implying the 5-minute poll means near-real-time incident coverage.
3. **Mapbox cost/key** — **Resolved**: switched to MapLibre GL JS (Mapbox GL JS's open-source fork, same API) styled with [OpenFreeMap](https://openfreemap.org) tiles, which needs no signup, API key, or credit card and has no usage cap — a better fit for a public/unauthenticated, always-on large-screen display than a metered Mapbox token.
4. **ECS Fargate may be more infra than this traffic needs** — Phase 1 is a small API plus a 5-minute batch job and a handful of large-screen clients. Following the spec's explicit ECS Fargate + Terraform choice as written; revisit cost/complexity once real usage is known.
5. **RDS Postgres may be oversized for data volume** — aviation incident volume is modest (hundreds–low thousands/year). Fully functional as specified; worth a cost/instance-sizing pass during Step 13 rather than defaulting to a larger instance class.
6. **Frontend/backend type drift** — `frontend/src/lib/types.ts` is hand-maintained to mirror the Pydantic schema. Consider generating TS types from FastAPI's OpenAPI schema (e.g. `openapi-typescript`) as a follow-up hardening step once Phase 1 stabilizes; not required for initial build.
7. **CSV export scope** — spec doesn't specify whether export covers the currently filtered view or the entire dataset. This plan uses a server-side `export.csv` endpoint honoring active filters; confirm this matches intent.

### Critical files to start with
- `backend/src/near_misses/models/incident.py`
- `backend/src/near_misses/ingestion/pipeline.py`
- `backend/src/near_misses/ingestion/faa_aids/` (and `ntsb/` fallback)
- `backend/src/near_misses/ws/manager.py`
- `infra/terraform/environments/dev/main.tf`

---

## Verification

- Backend: `pytest` (unit + api suites) green against docker-compose Postgres; `alembic upgrade head` runs cleanly from empty DB.
- Manual: `POST /api/poll/trigger` against the resolved data source populates the DB with at least one real or fixture-derived incident, archives the raw response to localstack S3, and pushes a WS message observable from a connected client.
- Frontend: `npm run build` + `tsc --noEmit` clean; Playwright E2E suite green against the docker-compose stack with a seeded DB.
- End-to-end manual check: load `/map` and confirm markers render and a live WS-pushed incident (triggered via manual poll) appears without a page refresh; navigate marker → modal → detail page; check `/dashboard` toggles and `/reports` filter+CSV export.
