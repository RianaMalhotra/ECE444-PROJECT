import pytest

from backtest_threshold import load_labelled, run_backtest, score_threshold


def test_load_labelled_skips_rows_without_type():
    rows = [
        {"confidence": "90", "type": "0"},
        {"confidence": "40", "type": "2"},
        {"confidence": "70", "type": ""},
    ]
    labelled, unlabelled = load_labelled(rows)
    assert labelled == [(90.0, True), (40.0, False)]
    assert unlabelled == 1


def test_score_threshold_counts():
    labelled = [(90, True), (60, True), (50, False), (20, False), (10, True)]
    result = score_threshold(labelled, 50)
    assert (result["true_positives"], result["false_positives"], result["false_negatives"]) == (2, 1, 1)
    assert result["precision"] == pytest.approx(2 / 3, abs=1e-4)
    assert result["recall"] == pytest.approx(2 / 3, abs=1e-4)


def test_run_backtest_picks_threshold_separating_classes():
    # Wildfires all score >= 70, non-wildfires all score <= 40.
    labelled = [(95, True), (80, True), (70, True), (40, False), (30, False), (10, False)]
    _, best = run_backtest(labelled, thresholds=[0, 25, 50, 75])
    assert best["threshold"] == 50
    assert best["f1"] == 1.0


def test_run_backtest_needs_data():
    with pytest.raises(ValueError):
        run_backtest([])
