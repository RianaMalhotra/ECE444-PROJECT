"""Database connection for the shared Supabase (PostgreSQL + PostGIS) database.

The connection string is read from the DATABASE_URL environment variable,
which is loaded from backend/.env (never committed). See backend/.env.example.
"""

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


class DatabaseNotConfigured(RuntimeError):
    """Raised when DATABASE_URL is not set."""


def get_database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise DatabaseNotConfigured(
            "DATABASE_URL is not set. Copy backend/.env.example to backend/.env and fill it in."
        )
    return url


def get_connection():
    """Open a new database connection. Use it with ``with get_connection() as conn:``."""
    return psycopg.connect(get_database_url(), connect_timeout=5)


def check_database():
    """Return (True, None) if the database answers, else (False, reason)."""
    try:
        with get_connection() as conn:
            conn.execute("select 1")
        return True, None
    except DatabaseNotConfigured as error:
        return False, str(error)
    except psycopg.Error:
        # Don't leak connection details (host, user) in the API response.
        return False, "Database is unavailable"
