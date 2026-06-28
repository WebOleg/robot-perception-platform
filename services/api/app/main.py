"""World B backend: ingests detections, persists them, serves them."""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .db import Detection, get_session, init_db
from .schemas import DetectionIn, DetectionOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="robot-perception-platform API",
    version="0.3.0",
    lifespan=lifespan,
)

# Allow the dashboard (browser) to call this API across origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/detections", response_model=DetectionOut, status_code=201)
def create_detection(
    payload: DetectionIn,
    session: Session = Depends(get_session),
) -> Detection:
    detection = Detection(**payload.model_dump())
    session.add(detection)
    session.commit()
    session.refresh(detection)
    return detection


@app.get("/detections", response_model=list[DetectionOut])
def list_detections(
    limit: int = 50,
    session: Session = Depends(get_session),
) -> list[Detection]:
    statement = (
        select(Detection).order_by(Detection.detected_at.desc()).limit(limit)
    )
    return list(session.exec(statement))
