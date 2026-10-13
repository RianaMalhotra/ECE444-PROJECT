"""Central configuration for the Flask backend.

Values can be overridden with environment variables so they are never
hardcoded in the detection logic (issue #19).
"""

import os

# Minimum FIRMS confidence (0-100) for a detection to be shown as a
# likely wildfire. Detections below this value are filtered out.
#
# 30 is PROVISIONAL: it is the lower bound of FIRMS's "nominal"
# confidence class. Replace it with the value recommended by
# ml/backtest_threshold.py once the backtest has been run on the
# historical FIRMS dataset, and record the result in docs/.
DEFAULT_MIN_DETECTION_CONFIDENCE = 30.0


def get_min_detection_confidence():
    """Return the configured threshold, falling back to the default.

    Set MIN_DETECTION_CONFIDENCE in the environment to override it, e.g.
    ``MIN_DETECTION_CONFIDENCE=50 python app.py``.
    """
    raw = os.environ.get("MIN_DETECTION_CONFIDENCE")
    if raw is None or raw.strip() == "":
        return DEFAULT_MIN_DETECTION_CONFIDENCE

    try:
        value = float(raw)
    except ValueError:
        raise ValueError(f"MIN_DETECTION_CONFIDENCE must be a number, got {raw!r}")

    if not 0 <= value <= 100:
        raise ValueError(f"MIN_DETECTION_CONFIDENCE must be between 0 and 100, got {value}")
    return value
