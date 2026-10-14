import pytest

from backtest_threshold import (
    label_by_persistence,
    load_labelled,
    run_backtest,
    score_threshold,
)


def row(lat, lon, timestamp, confidence):
    return {"latitude": str(lat), "longitude": str(lon), "timestamp": timestamp, "confidence": str(confidence)}


def test_load_labelled_skips_rows_without_type():
    rows = [
        {"confidence": "90", "type": "0"},
        {"confidence": "40", "type": "2"},
        {"confidence": "70", "type": ""},
    ]
    labelled, unlabelled = load_labelled(rows)
    assert labelled == [(90.0, True), (40.0, False)]
    assert unlabelled == 1


def test_persistence_confirms_fire_seen_again_nearby():
    rows = [
        row(55.0, -115.0, "2023-06-01T10:00:00Z", 80),   # seen again 1 km away a day later -> fire
        row(55.009, -115.0, "2023-06-02T10:00:00Z", 85),
        row(50.0, -100.0, "2023-06-01T10:00:00Z", 20),   # never seen again -> not confirmed
        row(40.0, -90.0, "2023-06-10T00:00:00Z", 50),    # late anchor so the others have a full window
    ]
    labelled, skipped = label_by_persistence(rows, radius_km=2, window_hours=72)
    assert labelled[0] == (80.0, True)
    assert labelled[2] == (20.0, False)
    # row 2 (Jun 2) is checked too; the last row is left out (no data after it)
    assert skipped == 1


def test_persistence_ignores_same_pass_and_far_or_late_detections():
    rows = [
        row(55.0, -115.0, "2023-06-01T10:00:00Z", 60),
        row(55.005, -115.0, "2023-06-01T10:00:00Z", 60),  # same pass: doesn't count
        row(55.1, -115.0, "2023-06-02T10:00:00Z", 60),    # ~11 km away: too far
        row(55.0, -115.0, "2023-06-06T10:00:00Z", 60),    # 5 days later: outside 72 h
        row(40.0, -90.0, "2023-06-20T00:00:00Z", 50),
    ]
    labelled, _ = label_by_persistence(rows, radius_km=2, window_hours=72)
    assert labelled[0] == (60.0, False)


def test_score_threshold_counts():
    labelled = [(90, True), (60, True), (50, False), (20, False), (10, True)]
    result = score_threshold(labelled, 50)
    assert (result["true_positives"], result["false_positives"],
            result["false_negatives"], result["true_negatives"]) == (2, 1, 1, 1)
    assert result["recall"] == pytest.approx(2 / 3, abs=1e-4)
    assert result["false_positive_rate"] == pytest.approx(0.5)
    assert result["youden_j"] == pytest.approx(2 / 3 - 0.5, abs=1e-4)


def test_run_backtest_picks_threshold_separating_classes():
    labelled = [(95, True), (80, True), (70, True), (40, False), (30, False), (10, False)]
    _, best = run_backtest(labelled, thresholds=[0, 25, 50, 75])
    assert best["threshold"] == 50
    assert best["youden_j"] == 1.0


def test_run_backtest_not_fooled_by_imbalance():
    # 95 real fires (mostly high confidence) vs 5 false hotspots (low confidence):
    # F1 would pick 0, Youden's J should pick a real cut-off.
    labelled = [(80, True)] * 90 + [(20, True)] * 5 + [(15, False)] * 5
    _, best = run_backtest(labelled, thresholds=[0, 10, 20, 50])
    assert best["threshold"] == 20


def test_run_backtest_rejects_single_label_data():
    with pytest.raises(ValueError):
        run_backtest([(90, True), (50, True)])
    with pytest.raises(ValueError):
        run_backtest([])


def test_min_recall_guard_prevents_dropping_too_many_fires():
    # Cutting at 75 removes all false hotspots but loses 30% of fires.
    labelled = [(80, True)] * 70 + [(40, True)] * 30 + [(30, False)] * 10 + [(70, False)] * 20
    _, unguarded = run_backtest(labelled, thresholds=[0, 35, 60, 75], min_recall=0.0)
    _, guarded = run_backtest(labelled, thresholds=[0, 35, 60, 75], min_recall=0.9)
    assert unguarded["threshold"] == 75
    assert guarded["threshold"] == 35
    assert guarded["recall"] >= 0.9
