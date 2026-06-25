"""API tests. Uses an in-memory SQLite DB shared across connections.

We override the app's get_session dependency with a test session bound to a
StaticPool engine, so the in-memory DB and its tables persist for the whole
test run (a plain sqlite:// loses tables between connections).
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite://")  # satisfies db.py import

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel, Session, create_engine  # noqa: E402
from sqlmodel.pool import StaticPool  # noqa: E402

from app.main import app  # noqa: E402
from app.db import get_session  # noqa: E402

# One in-memory DB, shared across all connections, for the whole test session.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(test_engine)


def override_get_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_list_detection():
    payload = {
        "label": "person", "confidence": 0.9,
        "x": 1, "y": 2, "width": 3, "height": 4,
    }
    r = client.post("/detections", json=payload)
    assert r.status_code == 201
    assert r.json()["id"] is not None
    assert r.json()["label"] == "person"

    r = client.get("/detections")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_rejects_invalid_confidence():
    bad = {"label": "x", "confidence": 1.5, "x": 0, "y": 0, "width": 1, "height": 1}
    r = client.post("/detections", json=bad)
    assert r.status_code == 422
