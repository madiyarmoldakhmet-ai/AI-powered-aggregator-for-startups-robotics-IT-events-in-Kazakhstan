from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app


Base.metadata.create_all(bind=engine)


def test_health() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_mock_events_are_available() -> None:
    with TestClient(app) as client:
        response = client.get("/events")
        assert response.status_code == 200
        assert len(response.json()) >= 3


def test_event_filter() -> None:
    with TestClient(app) as client:
        response = client.get("/events", params={"category": "robotics"})
        assert response.status_code == 200
        assert all(item["category"] == "robotics" for item in response.json())
