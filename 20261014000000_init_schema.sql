-- Initial schema for the Ash Detectives wildfire platform (Supabase / PostgreSQL + PostGIS).
-- Matches the shared-database design in docs/ECE444 PRA5 (Architecture Design):
-- detections, environmental observations, and risk assessment results.

create extension if not exists postgis with schema extensions;

-- ---------------------------------------------------------------------------
-- Wildfire detections (from NASA FIRMS, cleaned by data-processing/firms_cleaning.py)
-- ---------------------------------------------------------------------------
create table public.detections (
    id               bigint generated always as identity primary key,
    latitude         double precision not null check (latitude between -90 and 90),
    longitude        double precision not null check (longitude between -180 and 180),
    location         extensions.geography(point, 4326)
                     generated always as (
                         extensions.st_setsrid(extensions.st_makepoint(longitude, latitude), 4326)::extensions.geography
                     ) stored,
    detected_at      timestamptz not null,
    confidence       real not null check (confidence between 0 and 100),
    confidence_class text not null check (confidence_class in ('low', 'nominal', 'high')),
    instrument       text,
    satellite        text,
    frp              real,                -- fire radiative power (MW); null when unavailable
    daynight         text check (daynight in ('D', 'N')),
    fire_type        smallint check (fire_type between 0 and 3),  -- FIRMS archive "type"
    source           text not null default 'NASA FIRMS',
    created_at       timestamptz not null default now(),
    -- the same detection can appear in overlapping FIRMS downloads
    constraint detections_unique unique (latitude, longitude, detected_at, satellite)
);

create index detections_location_idx on public.detections using gist (location);
create index detections_detected_at_idx on public.detections (detected_at desc);
create index detections_confidence_idx on public.detections (confidence);

comment on table public.detections is 'Satellite fire detections (NASA FIRMS), cleaned before insert.';

-- ---------------------------------------------------------------------------
-- Monitored areas shown on the map
-- ---------------------------------------------------------------------------
create table public.areas (
    id          bigint generated always as identity primary key,
    name        text not null unique,
    latitude    double precision not null check (latitude between -90 and 90),
    longitude   double precision not null check (longitude between -180 and 180),
    location    extensions.geography(point, 4326)
                generated always as (
                    extensions.st_setsrid(extensions.st_makepoint(longitude, latitude), 4326)::extensions.geography
                ) stored,
    created_at  timestamptz not null default now()
);

create index areas_location_idx on public.areas using gist (location);

-- ---------------------------------------------------------------------------
-- Environmental observations per area (missing readings stay NULL, never made up: #27)
-- ---------------------------------------------------------------------------
create table public.environmental_observations (
    id                    bigint generated always as identity primary key,
    area_id               bigint not null references public.areas (id) on delete cascade,
    observed_at           timestamptz not null,
    temperature_c         real,
    relative_humidity_pct real check (relative_humidity_pct between 0 and 100),
    wind_speed_kmh        real check (wind_speed_kmh >= 0),
    precipitation_mm      real check (precipitation_mm >= 0),
    vegetation_index      real check (vegetation_index between -1 and 1),  -- e.g. NDVI
    source                text,
    created_at            timestamptz not null default now(),
    constraint environmental_observations_unique unique (area_id, observed_at, source)
);

create index environmental_observations_area_time_idx
    on public.environmental_observations (area_id, observed_at desc);

-- ---------------------------------------------------------------------------
-- Risk assessment results per area (#21, #28: incomplete results are flagged)
-- ---------------------------------------------------------------------------
create table public.risk_assessments (
    id             bigint generated always as identity primary key,
    area_id        bigint not null references public.areas (id) on delete cascade,
    assessed_at    timestamptz not null default now(),
    risk_score     real check (risk_score between 0 and 100),          -- null when it can't be computed
    risk_level     text check (risk_level in ('LOW', 'MODERATE', 'HIGH')),
    is_complete    boolean not null default false,
    missing_inputs text[] not null default '{}',                      -- e.g. {'wind_speed_kmh'}
    model_version  text,
    created_at     timestamptz not null default now(),
    -- a complete result must have a score and a level
    constraint risk_assessments_complete_has_score
        check (not is_complete or (risk_score is not null and risk_level is not null))
);

create index risk_assessments_area_time_idx on public.risk_assessments (area_id, assessed_at desc);

-- ---------------------------------------------------------------------------
-- Security: the Flask backend connects directly to Postgres, so the public
-- Supabase REST API does not need access. RLS on with no policies = no
-- access through the anon/authenticated API keys.
-- ---------------------------------------------------------------------------
alter table public.detections                 enable row level security;
alter table public.areas                      enable row level security;
alter table public.environmental_observations enable row level security;
alter table public.risk_assessments           enable row level security;
