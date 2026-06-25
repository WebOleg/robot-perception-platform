"""World B backend — FastAPI entry point.

Receives detections from the bridge, persists them to PostgreSQL
(the single source of truth), and serves them back to the dashboard.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlmodel import Session, select

from .db import Detection, get_session, init_db
from .schemas import DetectionIn, DetectionOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run once on startup: make sure tables exist."""
    init_db()
    yield


app = FastAPI(
    title="robot-perception-platform API",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Returns ok when the service is up."""
    return {"status": "ok"}


@app.post("/detections", response_model=DetectionOut, status_code=201)
def create_detection(
    payload: DetectionIn,
    session: Session = Depends(get_session),
) -> Detection:
    """Ingest one detection from the bridge.

    The payload is validated against the input contract before it ever
    reaches the database. Invalid data is rejected with a 422 automatically.
    """
    detection = Detection(**payload.model_dump())
    session.add(detection)
    session.commit()
    session.refresh(detection)  # reload to get the DB-assigned id
    return detection


@app.get("/detections", response_model=list[DetectionOut])
def list_detections(
    limit: int = 50,
    session: Session = Depends(get_session),
) -> list[Detection]:
    """Return the most recent detections, newest first."""
    statement = (
        select(Detection).order_by(Detection.detected_at.desc()).limit(limit)
    )
    return list(session.exec(statement))
