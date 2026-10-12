
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ok"
    assert data["message"] == "Wildfire Detection API is running"


def test_risk_areas_endpoint(client):
    response = client.get("/api/risk-areas")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["source"] == "mock"
    assert len(data["data"]) == 3

    for area in data["data"]:
        assert "latitude" in area
        assert "longitude" in area
        assert "risk_level" in area
