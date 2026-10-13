import pytest

import app as app_module
import db


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


def test_db_health_ok(client, monkeypatch):
    monkeypatch.setattr(app_module, "check_database", lambda: (True, None))
    response = client.get("/api/health/db")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_db_health_unavailable(client, monkeypatch):
    monkeypatch.setattr(app_module, "check_database", lambda: (False, "Database is unavailable"))
    response = client.get("/api/health/db")
    assert response.status_code == 503
    assert response.get_json() == {"status": "unavailable", "message": "Database is unavailable"}


def test_missing_database_url_is_reported(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    ok, reason = db.check_database()
    assert ok is False
    assert "DATABASE_URL is not set" in reason


def test_unreachable_database_hides_details(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@127.0.0.1:1/none")
    ok, reason = db.check_database()
    assert ok is False
    assert reason == "Database is unavailable"
    assert "secret" not in reason
