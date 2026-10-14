# Wildfire risk-scoring model (#21)

Code: `backend/services/risk_scoring.py` · API: `POST /api/risk-score` · Version: `weighted-index-v1`

## What it does

Combines environmental factors into one **0–100 risk score** per area, then maps it to the levels the map uses:

| Score | Level |
|---|---|
| 0 – 39.9 | LOW |
| 40 – 69.9 | MODERATE |
| 70 – 100 | HIGH |

## Factors and weights

Each input becomes a 0–100 "danger" sub-score (higher = more fire-prone). Sub-scores are combined with these weights:

| Factor | Input | 0 at… | 100 at… | Weight |
|---|---|---|---|---|
| Temperature | `temperature_c` | ≤ 5 °C | ≥ 35 °C | 0.15 |
| Humidity | `relative_humidity_pct` | ≥ 80 % | ≤ 15 % | 0.20 |
| Wind | `wind_speed_kmh` | 0 km/h | ≥ 50 km/h | 0.15 |
| Recent rain | `precipitation_mm` | ≥ 10 mm | 0 mm | 0.10 |
| Vegetation (fuel) | `vegetation_index` (NDVI) | ≤ 0.1 | ≥ 0.7 | 0.10 |
| Terrain | `slope_deg` | 0° | ≥ 30° | 0.05 |
| Fire history | `nearby_detections` | 0 | ≥ 1000 (log scale) | 0.25 |

The approach follows fire-danger indices such as Canada's Fire Weather Index (hot, dry, windy weather after little rain raises danger) and adds local fire history. **Fire history** is the number of NASA FIRMS detections (confidence ≥ the #19 threshold of 20) within **50 km**, counted from the Supabase `detections` table (2023–2025). On a log scale, 1 detection ≈ 10, 10 ≈ 35, 100 ≈ 67, 1000+ = 100.

## Missing inputs (#24, #28)

- Missing, `null` or out-of-range inputs are **never filled with made-up values**.
- The score uses the available factors, re-weighted to add up to 1, and the result has `is_complete: false` plus a `missing_inputs` list.
- If the available factors carry **less than 50 %** of the total weight, `risk_score` and `risk_level` are `null` (not enough information).
- If the database can't be reached, fire history is treated as a missing input; the API still answers.

## API

`POST /api/risk-score` with any of the inputs above. Give `latitude` and `longitude` instead of `nearby_detections` to have fire history looked up automatically.

```json
{ "temperature_c": 33, "relative_humidity_pct": 18, "wind_speed_kmh": 30,
  "precipitation_mm": 0, "vegetation_index": 0.45, "slope_deg": 12,
  "latitude": 49.888, "longitude": -119.496 }
```

Response (`data`): `risk_score`, `risk_level`, `is_complete`, `missing_inputs`, `coverage` (share of weight available), `factor_scores` (each factor's 0–100 sub-score), `model_version`.

Results can be stored with `save_assessment()` in the `risk_assessments` table.

## Examples (real fire-history counts from the database)

| Area and conditions | Nearby detections (50 km) | Score | Level |
|---|---|---|---|
| Kelowna, hot dry windy August day | 673 | 83.5 | HIGH |
| Toronto, mild June day | 21 | 44.3 | MODERATE |
| Ottawa, warm day, wind sensor missing | 22 | 59.1 | MODERATE (incomplete: `wind_speed_kmh`) |

## Limitations and next steps

- Weights and ranges are expert-set, not learned. Mild conditions can still reach MODERATE (e.g. Toronto above), so the level boundaries and weights should be tuned.
- **Sprint 2 ("improve model"):** fit the weights to data, e.g. a model trained on past weather vs. where FIRMS fires actually occurred, and validate against burned-area maps.
- Weather and vegetation inputs are not yet fetched automatically; a data source (e.g. Open-Meteo) still needs to be connected.
