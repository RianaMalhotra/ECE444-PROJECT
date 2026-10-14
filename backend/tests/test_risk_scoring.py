import pytest

import app as app_module
from services import risk_scoring
from services.risk_scoring import (
    WEIGHTS,
    count_nearby_detections,
    history_score,
    humidity_score,
    precipitation_score,
    risk_level,
    save_assessment,
    score_area,
    temperature_score,
)

ALL_INPUTS = {
    "temperature_c": 32,
    "relative_humidity_pct": 20,
    "wind_speed_kmh": 40,
    "precipitation_mm": 0,
    "vegetation_index": 0.6,
    "slope_deg": 15,
    "nearby_detections": 500,
}


def test_weights_add_up_to_one():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)


def test_factor_scores_point_the_right_way():
    assert temperature_score(35) > temperature_score(10)
    assert humidity_score(15) > humidity_score(80)          # drier = riskier
    assert precipitation_score(0) > precipitation_score(10)  # rain lowers risk
    assert history_score(1000) == 100 and history_score(0) == 0
    for value in (-100, 0, 20, 1000):
        assert 0 <= temperature_score(value) <= 100


@pytest.mark.parametrize("score, level", [
    (None, None), (0, "LOW"), (39.9, "LOW"), (40, "MODERATE"), (69.9, "MODERATE"), (70, "HIGH"), (100, "HIGH"),
])
def test_risk_level_boundaries(score, level):
    assert risk_level(score) == level


def test_hot_dry_windy_area_is_high_and_complete():
    result = score_area(ALL_INPUTS)
    assert result["risk_level"] == "HIGH"
    assert result["is_complete"] is True
    assert result["missing_inputs"] == []
    assert result["coverage"] == 1.0
    assert 0 <= result["risk_score"] <= 100


def test_cool_wet_calm_area_is_low():
    result = score_area({
        "temperature_c": 8, "relative_humidity_pct": 85, "wind_speed_kmh": 3,
        "precipitation_mm": 15, "vegetation_index": 0.2, "slope_deg": 1, "nearby_detections": 0,
    })
    assert result["risk_level"] == "LOW"


def test_missing_inputs_are_flagged_not_invented():
    partial = dict(ALL_INPUTS)
    del partial["wind_speed_kmh"]
    partial["slope_deg"] = None
    result = score_area(partial)
    assert result["is_complete"] is False
    assert set(result["missing_inputs"]) == {"wind_speed_kmh", "slope_deg"}
    assert "wind_speed_kmh" not in result["factor_scores"]
    assert result["risk_score"] is not None
    assert result["coverage"] == pytest.approx(0.80)


def test_invalid_values_count_as_missing():
    bad = dict(ALL_INPUTS, relative_humidity_pct=150, temperature_c="hot", wind_speed_kmh=True)
    result = score_area(bad)
    assert {"relative_humidity_pct", "temperature_c", "wind_speed_kmh"} <= set(result["missing_inputs"])


def test_too_little_data_gives_no_score():
    result = score_area({"slope_deg": 10, "vegetation_index": 0.5})  # only 15% of the weight
    assert result["risk_score"] is None
    assert result["risk_level"] is None
    assert result["is_complete"] is False


def test_empty_input():
    result = score_area({})
    assert result["risk_score"] is None
    assert len(result["missing_inputs"]) == len(WEIGHTS)


# --- database helpers (fake connection) ---

class FakeCursor:
    def __init__(self, row):
        self.row, self.calls = row, []

    def execute(self, sql, params):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.row

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConnection:
    def __init__(self, row):
        self.cur, self.committed = FakeCursor(row), False

    def cursor(self):
        return self.cur

    def commit(self):
        self.committed = True


def test_count_nearby_detections_uses_threshold_and_radius():
    conn = FakeConnection((42,))
    assert count_nearby_detections(conn, 49.9, -119.5, radius_km=50, min_confidence=20) == 42
    _, params = conn.cur.calls[0]
    assert params == {"lat": 49.9, "lon": -119.5, "radius_m": 50000, "min_confidence": 20}


def test_save_assessment_writes_and_commits():
    conn = FakeConnection((7,))
    result = score_area(ALL_INPUTS)
    assert save_assessment(conn, 3, result) == 7
    _, params = conn.cur.calls[0]
    assert params[0] == 3 and params[2] == "HIGH" and params[3] is True
    assert conn.committed


# --- API ---

@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


def test_api_scores_inputs(client):
    response = client.post("/api/risk-score", json=ALL_INPUTS)
    assert response.status_code == 200
    assert response.get_json()["data"]["risk_level"] == "HIGH"


def test_api_rejects_non_object_body(client):
    assert client.post("/api/risk-score", json=[1, 2]).status_code == 400
    assert client.post("/api/risk-score", data="not json").status_code == 400


def test_api_looks_up_history_from_location(client, monkeypatch):
    class DummyConn:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(app_module, "get_connection", lambda: DummyConn())
    monkeypatch.setattr(app_module, "count_nearby_detections", lambda conn, lat, lon: 539)
    body = {k: v for k, v in ALL_INPUTS.items() if k != "nearby_detections"}
    body.update(latitude=49.888, longitude=-119.496)
    data = client.post("/api/risk-score", json=body).get_json()["data"]
    assert "nearby_detections" in data["factor_scores"]


def test_api_database_down_means_history_missing(client, monkeypatch):
    def broken():
        raise RuntimeError("no database")

    monkeypatch.setattr(app_module, "get_connection", broken)
    body = {k: v for k, v in ALL_INPUTS.items() if k != "nearby_detections"}
    body.update(latitude=49.888, longitude=-119.496)
    response = client.post("/api/risk-score", json=body)
    assert response.status_code == 200
    assert "nearby_detections" in response.get_json()["data"]["missing_inputs"]
