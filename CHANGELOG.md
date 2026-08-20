# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Real-time Leaflet live map with vehicle markers, geofence overlays, and a click-to-pick location picker.
- Vehicle and geofence detail/edit pages.
- Automatic alert engine: geofence enter/exit, speeding, low battery, and offline detection.
- Authenticated WebSocket endpoints (`/ws/fleet`, `/ws/{vehicle_id}`).
- Alembic migrations, run automatically on container startup.
- Backend test suite (pytest, in-memory SQLite) covering auth, geofence math, the alert engine, and reporting.
- Frontend test suite (Jest + React Testing Library).
- GitHub Actions CI: lint, type-check, tests with coverage, and build for both stacks.
- Structured JSON logging and optional Sentry error tracking.
- `LICENSE`, `CONTRIBUTING.md`, this changelog, and a pinned backend dependency lockfile.

### Fixed
- MQTT ingestion pipeline was never wired to the tracking service; GPS data from devices went nowhere.
- Redis caching crashed every location write; Redis/MQTT hosts defaulted to `localhost`, unreachable from Docker.
- Alert `metadata` collided with SQLAlchemy's reserved `Base.metadata` attribute.
- Mosquitto silently rejected all cross-container connections without an explicit listener.
- WebSockets had no authentication; alerts and reports had no per-user ownership checks.
- `/auth/me` and `/auth/refresh` had request/response schema mismatches with the frontend.
- Vehicle "delete" only flipped a status flag instead of removing the record.

## [0.1.0] - 2026-08-18
Initial project skeleton: FastAPI backend, Next.js frontend, Docker Compose orchestration.
