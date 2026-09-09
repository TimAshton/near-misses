# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This repository currently contains no application code — only a README and a spec
(`_specs/SPEC.md`). There is no build, lint, or test tooling yet because no project
scaffold (frontend or backend) has been created. Do not assume a stack is already
in place; check for `package.json`, `pyproject.toml`, `requirements.txt`, `terraform/`,
etc. before running any commands, since these will be created as implementation begins.

## What this project is

"near-misses" is a planned large-screen web app ("US Incident Map") that overlays
public US incident data (aviation, seismic, weather, infrastructure) on an interactive
map. Full requirements, schema, and phased rollout plan live in `_specs/SPEC.md` —
read it before starting implementation work, since it defines scope, architecture, and
constraints in detail. Key points to know without re-reading the whole spec every time:

- **Phased build, gated on approval**: Phase 1 (aviation, via aviationweather.gov / NTSB)
  must be built and approved before Phase 2+ (rail, earthquakes, tsunamis, hurricanes)
  begins. Don't build later phases speculatively.
- **Normalized schema**: every incident source is expected to be transformed into one
  shared schema (id, source, category, event_type, severity, location, occurred_at,
  raw response, etc.) before storage — see the schema block in the spec.
- **Data pipeline shape**: scheduler (5 min) or manual trigger → fetch → validate →
  normalize → dedupe (by ID or source+occurred_at) → write to RDS → archive raw
  response to S3 → broadcast to clients over WebSocket.
- **Intended stack** (per spec, not yet present in repo): React + TypeScript (Vite),
  Mapbox GL JS, Tailwind, Recharts on the frontend; Python/FastAPI with
  APScheduler-or-Celery+Redis and SQLAlchemy on the backend; AWS RDS Postgres + S3
  for data; Terraform for all infrastructure (no manual AWS console changes).
- **Hard constraints**: US incidents only (reject non-US coordinates at ingestion), no
  auth/user accounts, free data sources only, all infra via Terraform.

## Commands

None yet — there is no build, lint, test, or run tooling in this repo. Once a
frontend/backend scaffold is added, this section should be updated with the actual
commands (e.g. `npm run dev`/`build`/`lint`, `pytest`, `terraform plan`).
