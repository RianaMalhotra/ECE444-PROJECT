import pytest
from services.detection_validation import validate_detection

@pytest.mark.parametrize("payload", [None, [], "unavailable", 0])
def test_unavailable_detection(payload):
    assert validate_detection(payload) == (False, "Detection data is unavailable")

@pytest.mark.parametrize("field", ["latitude", "longitude", "timestamp"])
def test_missing_field(field):
    payload = {"latitude": 45.4, "longitude": -78.3, "timestamp": "2026-10-10T12:00:00Z"}
    del payload[field]
    assert validate_detection(payload) == (False, f"Missing required field: {field}")

@pytest.mark.parametrize("field", ["latitude", "longitude", "timestamp"])
def test_null_field(field):
    payload = {"latitude": 45.4, "longitude": -78.3, "timestamp": "2026-10-10T12:00:00Z"}
    payload[field] = None
    assert validate_detection(payload) == (False, f"Missing required field: {field}")

@pytest.mark.parametrize("lat,lon", [(91, 0), (-91, 0), (0, 181), (0, -181), (True, 0), (0, False), ("45", 0)])
def test_invalid_coordinates(lat, lon):
    assert validate_detection({"latitude": lat, "longitude": lon, "timestamp": "2026-10-10T12:00:00Z"}) == (False, "Invalid coordinates")

@pytest.mark.parametrize("stamp", ["bad", "", 123, []])
def test_invalid_timestamp(stamp):
    assert validate_detection({"latitude": 45, "longitude": -78, "timestamp": stamp}) == (False, "Invalid timestamp")
