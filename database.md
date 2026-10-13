# Database (Supabase)

We use a hosted **PostgreSQL** database on **Supabase**, with the **PostGIS** extension for geographic queries. This follows the shared-database design in the PRA5 architecture document.

- **Project:** `ash-detectives`, in the `ECE444` Supabase organization (free plan)
- **Region:** `ca-central-1` (Canada)
- **Schema:** `supabase/migrations/20261014000000_init_schema.sql`

## Tables

| Table | What it stores |
|---|---|
| `detections` | Cleaned NASA FIRMS fire detections: location, time, confidence (0–100) and class, satellite, FRP, FIRMS type |
| `areas` | Monitored areas shown on the map (name + point location) |
| `environmental_observations` | Temperature, humidity, wind, precipitation and vegetation index per area over time; missing readings stay `NULL` (#27) |
| `risk_assessments` | Risk score and level per area; `is_complete` and `missing_inputs` flag results calculated without all inputs (#28) |

`detections` and `areas` have a generated `location` column (PostGIS `geography`) with a spatial index. That enables queries like "detections within 50 km of an area":

```sql
select d.*
from detections d
join areas a on a.name = 'Algonquin Provincial Park'
where extensions.st_dwithin(d.location, a.location, 50000);  -- metres
```

## Security

Row Level Security is **on** for every table, with no policies. That blocks the public Supabase REST API (anon key) completely. The Flask backend connects directly to Postgres with the database password, which is not affected by RLS. If the frontend ever needs to read directly from Supabase, add a specific read-only policy for that table.

## Connecting from the backend

1. Ask the team for the database password (or reset it: Supabase dashboard → Project Settings → Database).
2. Copy `backend/.env.example` to `backend/.env`.
3. In the dashboard, click **Connect** → **Session pooler** and paste that connection string into `DATABASE_URL`, with the password filled in.
4. Install the dependencies (`python -m pip install -r requirements.txt`) and run the backend.
5. Check `http://127.0.0.1:5000/api/health/db`. It should return `{"status": "ok"}`.

`backend/.env` is git-ignored. Never commit the password.

## Loading FIRMS data

```bash
python data-processing/firms_cleaning.py data-processing/data/fire_archive.csv data-processing/data/cleaned.csv
python data-processing/load_firms_to_db.py data-processing/data/cleaned.csv
```

Re-running the loader is safe: detections already in the table are skipped.

## Changing the schema

Add a new file to `supabase/migrations/` (don't edit the existing one), get it reviewed in a pull request, then apply it to the Supabase project.

## Free-plan note

Supabase pauses free projects after about a week with no activity. If the database stops responding, restore it from the dashboard.
