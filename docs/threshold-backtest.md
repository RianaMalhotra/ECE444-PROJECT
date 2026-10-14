# Detection confidence threshold: backtest results (#19)

**Chosen value:** `DEFAULT_MIN_DETECTION_CONFIDENCE = 20` in `backend/config.py` (provisional).
It can be overridden with the `MIN_DETECTION_CONFIDENCE` environment variable.

## Data

NASA FIRMS **MODIS Collection 6.1**, standard-processing country yearly summaries for **Canada**. Raw files are not committed; see `data-processing/README.md` to download them.

| Year | Detections (all kept after cleaning) |
|---|---|
| 2023 | 324,003 |
| 2024 | 147,547 |
| 2025 | 156,313 |

## Method

1. Clean each file with `data-processing/firms_cleaning.py`.
2. **Answer key (persistence):** a detection counts as a real fire if another detection is within **2 km**, **1–72 hours later**. Real fires keep burning and are detected again; one-off false hotspots are not. Detections in the last 72 hours of the data are left out because they can't be confirmed.
3. Score thresholds 0–100 (step 5) and recommend the one with the best **Youden's J** (recall minus false-positive rate) among thresholds that keep **at least 90% of real fires**. For early detection, missing a fire is worse than a false alarm.

The FIRMS `type` column was tried first, but ~99.9% of Canadian detections are type 0 ("presumed vegetation fire"), so it could not separate thresholds.

## Results

| Year | Real fires / one-offs | Recommended | Recall | One-offs still kept | Youden's J |
|---|---|---|---|---|---|
| 2023 | 263,563 / 60,406 | **20** | 0.911 | 0.873 | 0.038 |
| 2024 | 119,773 / 27,699 | **20** | 0.908 | 0.890 | 0.018 |
| 2025 | 123,353 / 32,946 | **15** | 0.900 | 0.887 | 0.013 |

The recommendation is stable across three seasons (15–20), so **20** was chosen.

2023 trade-off across thresholds (share kept):

| Threshold | 0 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Real fires | 1.00 | 0.93 | 0.91 | 0.88 | 0.82 | 0.76 | 0.69 | 0.60 | 0.49 | 0.37 | 0.24 |
| One-off hotspots | 1.00 | 0.90 | 0.87 | 0.83 | 0.76 | 0.68 | 0.58 | 0.48 | 0.36 | 0.24 | 0.14 |

## Limitations

- **Confidence alone is a weak filter.** Real fires and one-off hotspots are dropped at nearly the same rate as the threshold rises. The best separation (J = 0.13 at 80) would discard half of all real fires. Precision only rises from 0.81 to 0.88 across the full range.
- **Persistence is a proxy, not field-verified truth.** Short-lived real fires count as "one-offs", and a false hotspot next to a real fire can be counted as real.
- **Next step:** combine confidence with other signals (repeat detection, FRP, land cover), or validate against official burned-area perimeters (e.g. NBAC).

## Reproduce

```bash
python data-processing/firms_cleaning.py data-processing/data/modis_2023_Canada.csv data-processing/data/cleaned_2023.csv
python ml/backtest_threshold.py data-processing/data/cleaned_2023.csv data-processing/data/backtest_2023.csv
```
