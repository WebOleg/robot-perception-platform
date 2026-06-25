# robot-perception-platform

A robotics perception platform: a simulated robot perceives objects through a
camera, and the system streams those detections into a cloud backend with a
live dashboard.

The design splits cleanly into two decoupled domains joined by a single seam.

## Architecture at a glance

    World A (robot)  -->  Bridge (the seam)  -->  World B (web)

- World A — robot domain (robot/): real-time, stateless ROS2 nodes.
  Camera and perception (OpenCV + YOLO). Heavy data (frames) never leaves here.
- The seam (bridge/): the only component touching both worlds. Translates
  ROS2 messages into network calls. Swap either side without touching the other.
- World B — web domain (services/, web/): stateful. Go backend,
  PostgreSQL as the single source of truth, React dashboard.

## Core principles

1. Two domains, one seam — the worlds never couple directly.
2. One component, one responsibility — composable, not welded.
3. Robot is stateless; web is stateful; the DB is the single source of truth.
4. Heavy data stays local; only light structured facts cross the network.
5. Nothing hardcoded — all secrets via environment variables.
6. Everything containerized and horizontally scalable.
7. Explicit contracts between components.

See docs/architecture.md for the full rationale.

## Repository layout

- robot/     (World A)  ROS2 nodes: camera, perception
- bridge/    (the seam) ROS2 -> network translation
- services/  (World B)  stateful backend services (Go)
- web/       (World B)  React/Next.js dashboard
- infra/     (ops)      Docker Compose, CI/CD, deployment
- docs/                 architecture and design decisions

## Status

Early scaffold. Built incrementally, phase by phase.
