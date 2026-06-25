# Architecture

## Two worlds, one seam

The system is two separate systems that speak different languages, joined at
exactly one point.

- World A — the robot. Everything communicates via ROS2 topics and messages.
  Real-time, stream-oriented, deals in binary frames. No databases, no HTTP.
- World B — the web. REST, JSON, PostgreSQL, a browser frontend.
  Request/response, persistent state.

The two worlds must not know about each other. The robot does not know a
database exists. The backend does not know what a ROS2 topic is. The only point
of contact is the Bridge. Replace the entire robot with real hardware and
World B never notices — that is the seam working.

## One node, one responsibility

World A is many small nodes, each doing exactly one thing — the same thinking as
microservices.

- camera node: produce frames, publish to a topic. Knows nothing about YOLO.
- perception node: consume frames, detect objects, publish detections. Knows
  nothing about the camera source or the network.
- bridge node: consume detections, send them out over HTTP/MQTT. Knows nothing
  about the camera or YOLO.

Any link can be swapped, tested, and scaled independently.

## Data shape along the pipeline

- A binary frame (heavy, hundreds of KB) lives only inside World A.
- After YOLO it collapses into a light structured fact:
  class, confidence, bounding box, timestamp — a small JSON object.
- That fact crosses the seam, lands as a row in PostgreSQL, and is served to
  the frontend as a list item via the API.

The seam sits exactly where data becomes cheap and structured. Heavy stays
local; only conclusions travel the network.

## Where state lives

- World A is stateless. A node processes a frame and forgets it. Crash and
  restart loses nothing because there is nothing to lose.
- World B is stateful. All memory — detection history, settings — lives only
  in PostgreSQL. Single source of truth.
- The Bridge handles delivery failures with retries, backoff and idempotency,
  so the source of truth stays consistent.

## Deployment topology

Three logical groups, all containerized:

1. Robot/simulation (Gazebo + ROS2 nodes) — CPU/GPU heavy; in production
   lives near the robot or on an edge device.
2. Bridge — thin; the only component with a foot in both networks.
3. Web stack (backend + PostgreSQL + frontend) — standard, scales
   horizontally; in production goes to the cloud.

The edge/cloud boundary follows the same line as the domain boundary.
