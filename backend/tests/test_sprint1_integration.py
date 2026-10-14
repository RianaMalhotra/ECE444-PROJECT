"""Sprint 1 API integration checks; no live Supabase credentials required."""
import app as app_module


def test_risk_areas_frontend_contract():
    with app_module.app.test_client() as client:
        response = client.get("/api/risk-areas")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["source"] == "mock"
    assert isinstance(payload["data"], list)
    for area in payload["data"]:
        assert isinstance(area["id"], int)
        assert isinstance(area["latitude"], (int, float))
        assert isinstance(area["longitude"], (int, float))
        assert -90 <= area["latitude"] <= 90
        assert -180 <= area["longitude"] <= 180
        assert area["risk_level"] in {"LOW", "MODERATE", "HIGH"}


def test_database_health_success(monkeypatch):
    monkeypatch.setattr(app_module, "check_database", lambda: (True, None))
    with app_module.app.test_client() as client:
        response = client.get("/api/health/db")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_database_health_failure(monkeypatch):
    monkeypatch.setattr(app_module, "check_database", lambda: (False, "Database is unavailable"))
    with app_module.app.test_client() as client:
        response = client.get("/api/health/db")
    assert response.status_code == 503
    assert response.get_json()["status"] == "unavailable"
