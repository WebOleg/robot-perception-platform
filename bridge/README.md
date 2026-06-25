# bridge/ — the seam

The only component that touches both worlds. Subscribes to ROS2 detection
topics and forwards light structured facts to World B over HTTP/MQTT.

Handles delivery reliability (retries, backoff, idempotency). Replace either
side of the system without changing the other.
