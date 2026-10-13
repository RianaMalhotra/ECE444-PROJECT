"""Backtest the detection confidence threshold on historical FIRMS data (#19).

The question: which minimum confidence keeps the most real wildfire
detections while filtering out the most false ones?

Ground truth used here
----------------------
The FIRMS *archive* (not the near-real-time feed) includes a ``type``
column that classifies each detection after the fact:

    0 = presumed vegetation fire   -> counted as a real wildfire
    1 = active volcano             -> not a wildfire
    2 = other static land source   -> not a wildfire (e.g. gas flares, industry)
    3 = offshore                   -> not a wildfire

This is a proxy, not field-verified truth, so the result is a
*provisional* starting value. Rows without a ``type`` cannot be labelled
and are left out of the scoring (and counted in the report).

Usage (from the repository root), after cleaning the raw archive file:

    python data-processing/firms_cleaning.py fire_archive.csv cleaned.csv
    python ml/backtest_threshold.py cleaned.csv backtest_results.csv
"""

import csv
import sys

WILDFIRE_TYPE = "0"
DEFAULT_THRESHOLDS = list(range(0, 101, 5))


def load_labelled(rows):
    """Return (list of (confidence, is_wildfire), number of unlabelled rows)."""
    labelled, unlabelled = [], 0
    for row in rows:
        fire_type = (row.get("type") or "").strip()
        confidence = (row.get("confidence") or "").strip()
        if fire_type == "" or confidence == "":
            unlabelled += 1
            continue
        try:
            score = float(confidence)
        except ValueError:
            unlabelled += 1
            continue
        labelled.append((score, fire_type == WILDFIRE_TYPE))
    return labelled, unlabelled


def score_threshold(labelled, threshold):
    """Precision, recall and F1 when keeping detections >= threshold."""
    tp = fp = fn = 0
    for confidence, is_wildfire in labelled:
        kept = confidence >= threshold
        if kept and is_wildfire:
            tp += 1
        elif kept and not is_wildfire:
            fp += 1
        elif not kept and is_wildfire:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    kept_share = (tp + fp) / len(labelled) if labelled else 0.0
    return {
        "threshold": threshold,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "kept_share": round(kept_share, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
    }


def run_backtest(labelled, thresholds=None):
    """Score every threshold and pick the one with the best F1.

    Ties go to the higher threshold (fewer false alarms for the same F1).
    """
    if not labelled:
        raise ValueError("No labelled rows: the backtest needs FIRMS archive data with a 'type' column.")
    results = [score_threshold(labelled, t) for t in (thresholds or DEFAULT_THRESHOLDS)]
    best = max(results, key=lambda r: (r["f1"], r["threshold"]))
    return results, best


def main(input_path, output_path):
    with open(input_path, newline="", encoding="utf-8") as source:
        labelled, unlabelled = load_labelled(csv.DictReader(source))

    results, best = run_backtest(labelled)

    with open(output_path, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    wildfires = sum(1 for _, is_fire in labelled if is_fire)
    print(f"Scored {len(labelled)} labelled detections ({wildfires} presumed wildfires); "
          f"skipped {unlabelled} without a label.")
    print(f"Recommended provisional threshold: {best['threshold']} "
          f"(precision {best['precision']}, recall {best['recall']}, F1 {best['f1']}).")
    print(f"Full results written to {output_path}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ml/backtest_threshold.py <cleaned.csv> <results.csv>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
