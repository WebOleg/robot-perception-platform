# ADR 0001: Separate service for annotated frames

## Status
Accepted

## Context
The system already moves lightweight detection facts (label, confidence, bbox)
from World A (robot) to World B (web) through the bridge and stores them in
PostgreSQL. We now want to visualise perception: show the actual frame with
bounding boxes / segmentation masks drawn on it.

An annotated frame is heavy binary data with a different lifecycle from a
detection fact: it is large, ephemeral (only "now" matters), and must not be
persisted. Routing it through the existing facts path (bridge -> api -> DB)
would violate two core principles:
- #1 decoupled domains / single responsibility: the API owns facts, not media.
- #4 heavy data stays local; only light facts cross the network and reach the DB.

## Decision
Introduce a dedicated frame-service for the heavy media path, parallel to the
existing facts path. The two paths are independent:

- Facts:  detector --/detections (JSON)--> bridge --HTTP--> api --> PostgreSQL
- Frames: detector --/annotated (CompressedImage)--> frame-service --HTTP(JPEG)--> dashboard

The detector publishes an annotated frame to a separate ROS2 topic
(/annotated, sensor_msgs/CompressedImage). The frame-service subscribes, keeps
only the latest frame in memory, and serves it over HTTP. Frames are never
written to the database. The dashboard shows the live frame next to the table
of facts read from the API.

## Consequences
Positive:
- Domains stay decoupled; API remains the single source of truth for facts only.
- Principle #4 preserved: frames never hit the DB; heavy data isolated in memory.
- Symmetric, explicit contracts: one path per data nature (facts vs media).
- Segmentation vs boxes is just a model/draw change in the detector; the
  transport and services are unaffected.

Negative / limits:
- One more service to run, build, and test (acceptable; mirrors the bridge).
- Shipping JPEG over a ROS2 topic is fine at ~1 fps (our case). For high-fps
  production video a streaming protocol (WebRTC/RTSP) would be used instead;
  this is a deliberate scope choice for a low-rate demo, not the general design.

## Contract
- Topic: /annotated
- Type: sensor_msgs/msg/CompressedImage (JPEG)
- frame-service endpoint: GET /frame -> image/jpeg (latest frame, 404 if none yet)
