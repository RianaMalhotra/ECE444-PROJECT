# Data processing

## NASA FIRMS cleaning (`firms_cleaning.py`)

Cleans raw NASA FIRMS active-fire CSVs (MODIS or VIIRS) into one consistent format for model input.

**What it does**
- Converts MODIS (0–100) and VIIRS (`l`/`n`/`h`) confidence into one 0–100 score plus a `low`/`nominal`/`high` class
- Combines `acq_date` and `acq_time` into one UTC ISO timestamp (handles times stored without leading zeros)
- Drops rows with invalid coordinates, dates or confidence, and reports how many were dropped and why
- Removes duplicate detections
- Leaves missing optional values (such as `frp`) empty instead of filling in a made-up number (#27)

**Getting the data**
1. Go to https://firms.modaps.eosdis.nasa.gov/download/ and request an archive download (free NASA Earthdata login).
2. Choose a region (e.g. Canada) and date range, MODIS or VIIRS, CSV format.
3. Save the CSV in `data-processing/data/`. That folder is git-ignored, so raw data is never committed.

Use the **archive** data, not near-real-time: only the archive includes the `type` column needed for the threshold backtest.

**Run**
```bash
python data-processing/firms_cleaning.py data-processing/data/fire_archive.csv data-processing/data/cleaned.csv
```

## Threshold backtest (`ml/backtest_threshold.py`, issue #19)

```bash
python ml/backtest_threshold.py data-processing/data/cleaned.csv data-processing/data/backtest_results.csv
```

It scores thresholds from 0 to 100 (step 5) using FIRMS `type = 0` (presumed vegetation fire) as the positive label, and recommends the threshold with the best F1. Put the recommended value in `DEFAULT_MIN_DETECTION_CONFIDENCE` in `backend/config.py`. The threshold can also be overridden at runtime with the `MIN_DETECTION_CONFIDENCE` environment variable.

## Tests

```bash
python -m pytest tests          # data-processing and backtest tests (from repo root)
cd backend && python -m pytest  # backend tests, including the threshold filter
```
