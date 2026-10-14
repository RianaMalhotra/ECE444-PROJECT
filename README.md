# Wildfire Early Detection and Risk Assessment

**Team Ash Detectives | ECE444 Software Engineering | University of Toronto**

> **Status: Active development (October 2026).** The React/Flask prototype works with **three mock risk areas**. Risk scoring, FIRMS cleaning, a configurable confidence threshold, and Supabase/PostGIS integration code exist separately. **This is not a live wildfire monitoring or emergency alert system.**

## Current implementation

| Feature | Status | What it actually does |
| --- | --- | --- |
| React/Vite frontend | Implemented | Interactive Leaflet map with OpenStreetMap tiles |
| Risk heatmap (#22) | Prototype | Three colored circular regions (HIGH, MODERATE, LOW), not a continuous heatmap |
| React–Flask integration | Implemented | Fetches `GET /api/risk-areas` and displays loading/error/demo-data notices |
| Risk areas endpoint | Mock | Returns three static coordinates and risk levels with `source: "mock"` |
| Detection validation (#20) | Implemented | Rejects missing/invalid coordinates, timestamps and unavailable input |
| Weighted risk scoring (#21) | Implemented separately | Calculates a 0–100 score from seven factors; **not yet connected to the map** |
| Confidence threshold (#19) | Implemented | Configurable `MIN_DETECTION_CONFIDENCE`, currently defaulting to **20**; provisional backtest |
| NASA FIRMS processing | Scripts implemented | Cleaning, normalization, deduplication and database loading utilities |
| Supabase PostgreSQL/PostGIS | Schema and connector implemented | Database connectivity and population must be verified in the actual environment |
| Automated testing | Tests implemented | Backend pytest coverage for APIs, validation, risk scoring and mocked database checks |

**Detection confidence and wildfire risk are different measures.** The displayed mock risk levels are neither real detection confidence nor calculated live environmental risk.

## API (Flask: backend/app.py)

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/api/health` | Flask application health |
| GET | `/api/health/db` | Database check: HTTP 200 when reachable, HTTP 503 otherwise |
| GET | `/api/risk-areas` | Three static demo risk areas |
| POST | `/api/risk-score` | Weighted score from supplied JSON environmental inputs; optionally queries nearby detections when coordinates are given |

The risk-scoring response contains `risk_score`, `risk_level`, `is_complete`, `missing_inputs`, `coverage`, `factor_scores` and `model_version`. Missing inputs are not fabricated; insufficient coverage results in a null score. The current model is a first-version heuristic, **not a validated wildfire forecast**.

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/risk-score -H "Content-Type: application/json" -d '{"temperature_c":32,"relative_humidity_pct":20,"wind_speed_kmh":40,"precipitation_mm":0,"vegetation_index":0.6,"slope_deg":15,"nearby_detections":500}'
```

## Architecture: current connections

```text
React + Leaflet -> frontend/src/services/riskApi.js
                -> Flask GET /api/risk-areas -> three mock circles

Separate backend functionality:
JSON inputs -> POST /api/risk-score -> weighted risk model
                                   -> optional Supabase/PostGIS fire-history lookup

NASA FIRMS CSV -> cleaning script -> optional database loader -> PostgreSQL
```

The database schema defines detections, monitored areas, environmental observations and risk assessments. It does not establish that ingestion or model evaluation runs automatically.

## Getting started

Prerequisites: Git, Python 3, a modern Node.js version and npm.

```bash
git clone https://github.com/RianaMalhotra/ECE444-PROJECT.git
cd ECE444-PROJECT
```

**Backend (first terminal):**

```bash
cd backend
python -m venv .venv
```

Activate: Windows PowerShell `.\.venv\Scripts\Activate.ps1`; macOS/Linux `source .venv/bin/activate`.

```bash
python -m pip install -r requirements.txt
python app.py
```

Check `http://127.0.0.1:5000/api/health` and `http://127.0.0.1:5000/api/risk-areas`. The mock map does **not** require Supabase.

**Frontend (second terminal, from the repository root):**

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173` (or the URL printed by Vite). The map should show three colored demo circles; clicking a circle displays its risk level and coordinates. With Flask stopped, the UI should show an error.

The frontend currently hardcodes Flask at `http://127.0.0.1:5000`. Flask CORS currently permits `http://localhost:5173`.

### Optional database setup

Follow [docs/database.md](docs/database.md). Copy `backend/.env.example` to `backend/.env` and insert the **current** Supabase Session pooler connection string and password. Do not assume the example URL is correct. Never commit credentials.

Run Flask and check `http://127.0.0.1:5000/api/health/db`. A 503 means the connection is not confirmed. The migration is at `supabase/migrations/20261014000000_init_schema.sql`.

### FIRMS cleaning

From the repository root:

```bash
python data-processing/firms_cleaning.py path/to/raw.csv path/to/cleaned.csv
```

The script handles MODIS numeric confidence and VIIRS confidence classes. VIIRS classes are mapped to approximate numeric values; these are assumptions, not original VIIRS confidence scores. For loading cleaned rows, see [docs/database.md](docs/database.md).

## Testing

Backend, from `backend/`:

```bash
python -m pytest -q
```

Frontend, from `frontend/`:

```bash
npm run build
npm run lint
```

See [docs/sprint1-verification.md](docs/sprint1-verification.md) for browser and database smoke checks. Database health tests use mocks; passing tests does **not** prove the live Supabase instance is reachable. This README update does not claim that the full suite or build has been executed.

Additional tests for issues #20 and #22 were proposed in PR #41. Their inclusion in `main` depends on whether that PR has been merged.

## Key repository paths

- `frontend/src/App.jsx` — Leaflet map, circles, popups and UI states
- `frontend/src/services/riskApi.js` — Flask API client
- `backend/app.py` — Flask endpoints
- `backend/services/detection_validation.py` — input validation
- `backend/services/risk_scoring.py` — weighted risk model and database helpers
- `backend/config.py` — configurable confidence threshold
- `backend/db.py` — PostgreSQL connection and health check
- `backend/tests/` — pytest tests
- `data-processing/firms_cleaning.py` — NASA FIRMS cleaning
- `data-processing/load_firms_to_db.py` — database loader
- `ml/` — model/backtest code
- `supabase/migrations/` — PostGIS schema
- `docs/database.md` — Supabase setup
- `docs/threshold-backtest.md` — threshold evaluation
- `docs/requirements.md` — requirements and acceptance criteria

## Not yet complete

- Feed real environmental observations and risk assessments into the map instead of mock areas.
- Connect FIRMS processing, classification and risk scoring into a verified end-to-end pipeline.
- Display area-specific calculated risk factors and detection confidence separately.
- Verify the shared database connection, migrations and data ingestion.
- Improve map visualization beyond three fixed-radius circles.
- Expand CI, frontend rendering tests, error handling and model evaluation.

**Safety limitation:** The application does not provide verified real-time detections, emergency alerts, or validated forecasts. Do not use it for emergency decisions.

## Team and collaboration

Team Ash Detectives uses [GitHub Issues](https://github.com/RianaMalhotra/ECE444-PROJECT/issues), [GitHub Projects](https://github.com/users/RianaMalhotra/projects/1) and peer-reviewed pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [team_workflow.md](team_workflow.md), and [team_members.md](team_members.md).
