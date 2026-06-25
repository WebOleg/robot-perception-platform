"""World B backend — FastAPI entry point.

Starts minimal: a health endpoint that proves the service is alive.
Detection ingestion and persistence are added in later steps.
"""
from fastapi import FastAPI

app = FastAPI(
    title="robot-perception-platform API",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Returns ok when the service is up."""
    return {"status": "ok"}
