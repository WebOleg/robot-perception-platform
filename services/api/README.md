# services/api — World B (backend)

Stateful Go service. Receives detections from the bridge, validates them, and
persists to PostgreSQL (the single source of truth). Exposes a REST API.

New backend capabilities go as sibling services under services/.
