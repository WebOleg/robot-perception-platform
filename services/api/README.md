# services/api — World B (backend)

Stateful Python (FastAPI) service. Receives detections from the bridge,
validates them, and persists to PostgreSQL (the single source of truth).
Exposes a REST API.

New backend capabilities go as sibling services under services/.

## Run locally (via Docker)

    docker compose up api

Health check: GET /health
