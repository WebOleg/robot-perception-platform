"""Database layer (principle #3: the DB is the single source of truth).

Owns the engine, the table definition, and session handling. Nothing here
knows about HTTP — it only knows how to persist and fetch detections.
"""
import os
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, create_engine, Session


# Connection string comes from the environment (principle #5: nothing hardcoded).
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


class Detection(SQLModel, table=True):
    """The detections table. One row = one object the robot saw."""

    id: int | None = Field(default=None, primary_key=True)
    label: str = Field(index=True)
    confidence: float
    x: float
    y: float
    width: float
    height: float
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )


def init_db() -> None:
    """Create tables if they do not exist yet. Called on startup."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Yield a DB session per request (FastAPI dependency)."""
    with Session(engine) as session:
        yield session
