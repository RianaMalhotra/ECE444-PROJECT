"""Diagnose why the backend can't reach our Supabase database.

Put this file in backend/ and run it from anywhere:

    python backend/check_db.py

It checks each step in order and stops at the first problem, printing what
went wrong and how to fix it. The password is never printed.
"""

import os
import socket
import sys
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(HERE, ".env")


def fail(step, problem, fix):
    print(f"\n[FAIL] {step}\n  Problem: {problem}\n  Fix:     {fix}")
    sys.exit(1)


def ok(step, detail=""):
    print(f"[ OK ] {step}" + (f"  ({detail})" if detail else ""))


# 1. Are we on a branch that has the database code?
if not os.path.exists(os.path.join(HERE, "db.py")):
    fail("Database code present",
         "backend/db.py does not exist, so your copy is older than the Supabase setup "
         "(merged into main in PRs #36 and #37).",
         "git switch main, then git pull")
ok("Database code present", "backend/db.py found")

# 2. Python packages
try:
    import psycopg  # noqa: F401
    from dotenv import load_dotenv
except ImportError as error:
    fail("Python packages",
         f"{error}. The packages are installed for a different Python than the one running this script.",
         f"{sys.executable} -m pip install -r {os.path.join(HERE, 'requirements.txt')}")
ok("Python packages", f"psycopg {psycopg.__version__}, using {sys.executable}")

# 3. .env file and DATABASE_URL
if not os.path.exists(ENV_PATH):
    fail(".env file",
         f"{ENV_PATH} does not exist. It is git-ignored, so it never comes with git pull.",
         "Copy backend/.env.example to backend/.env and paste the Session pooler string into DATABASE_URL.")
load_dotenv(ENV_PATH, override=True)
url = os.environ.get("DATABASE_URL", "").strip()
if not url:
    fail("DATABASE_URL", "backend/.env exists but DATABASE_URL is empty or misspelled.",
         "The line must be exactly DATABASE_URL=postgresql://... with no spaces around '='.")
if (url[0] == url[-1]) and url[0] in "\"'":
    url = url[1:-1]
ok(".env file", "DATABASE_URL is set")

# 4. Shape of the connection string
if "[YOUR-PASSWORD]" in url or "[" in url or "]" in url:
    fail("Connection string", "It still contains [YOUR-PASSWORD] or square brackets.",
         "Replace [YOUR-PASSWORD] (including the brackets) with the real database password.")
try:
    parts = urlparse(url)
    host, port = parts.hostname, parts.port or 5432
    user, password = parts.username, parts.password
except ValueError as error:
    fail("Connection string", f"Can't be parsed ({error}). Usually the password contains @ : / # ? or %.",
         "URL-encode those characters in the password (@ -> %40, # -> %23, / -> %2F, : -> %3A, ? -> %3F, % -> %25), "
         "or reset the DB password to letters and digits only (tell the team if you do).")
if url.count("@") > 1 or "#" in url or "?" in url.split("@")[0] or (host and "." not in host):
    fail("Connection string",
         "The password contains a special character (@ # ? / :) that breaks the URL, so the host is read wrong.",
         "URL-encode it in the password (@ -> %40, # -> %23, ? -> %3F, / -> %2F, : -> %3A, % -> %25), "
         "or reset the DB password to letters and digits only (tell the team if you do).")
if parts.scheme not in ("postgresql", "postgres"):
    fail("Connection string", f"It starts with '{parts.scheme}://' instead of 'postgresql://'.",
         "Copy the URI version of the string from Supabase -> Connect.")
if not host or not password:
    fail("Connection string", "Host or password is missing. Likely an unencoded @ in the password.",
         "URL-encode the password (@ -> %40) or reset it to letters and digits only.")
if host.startswith("db.") and host.endswith(".supabase.co"):
    fail("Connection string",
         f"This is the Direct connection host ({host}). It is IPv6-only and fails on most home/campus networks.",
         "Supabase dashboard -> Connect -> 'Session pooler' and copy that string instead.")
if "pooler.supabase.com" in host and user and not user.startswith("postgres."):
    fail("Connection string", f"Pooler connections need the user 'postgres.<project-ref>', not '{user}'.",
         "Copy the full Session pooler string again; don't edit the user part.")
ok("Connection string", f"user={user}, host={host}, port={port}")

# 5. Can this network see the host at all?
try:
    addresses = {info[4][0] for info in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
except socket.gaierror as error:
    fail("DNS lookup", f"{host} could not be resolved ({error}).",
         "Check for typos in the host, and that you are online (try a different network or a phone hotspot).")
ok("DNS lookup", ", ".join(sorted(addresses))[:80])

try:
    with socket.create_connection((host, port), timeout=6):
        pass
except OSError as error:
    fail("Network connection", f"Can't open a connection to {host}:{port} ({error}).",
         "This network blocks the port (common on campus, office and some VPN networks). "
         "Try a phone hotspot or home Wi-Fi, or turn off the VPN. Also check the project isn't paused "
         "(Supabase pauses free projects after ~1 week idle: dashboard -> Restore project).")
ok("Network connection", f"{host}:{port} reachable")

# 6. Log in and query
try:
    with psycopg.connect(url, connect_timeout=8) as conn:
        version = conn.execute("select extensions.postgis_version()").fetchone()[0]
        count = conn.execute("select count(*) from public.detections").fetchone()[0]
except psycopg.OperationalError as error:
    message = str(error).strip().splitlines()[0] if str(error).strip() else repr(error)
    lower = message.lower()
    if "password authentication failed" in lower:
        fix = ("Wrong password. Get the current one from whoever manages the project (it may have been reset); "
               "don't reset it yourself without telling the team, or everyone else's .env breaks.")
    elif "tenant or user not found" in lower:
        fix = "The project ref in the user name or the pooler region is wrong. Copy the Session pooler string again."
    elif "timeout" in lower or "timed out" in lower:
        fix = "Connection is too slow or blocked. Try another network, and check the project isn't paused."
    else:
        fix = "Send this exact message to the team chat."
    fail("Database login", message.replace(unquote(password), "****"), fix)
except psycopg.errors.UndefinedTable:
    fail("Tables", "Connected, but the detections table doesn't exist in this database.",
         "You may be connected to a different Supabase project. Use the 'ash-detectives' project's string.")
except psycopg.Error as error:
    fail("Query", str(error).replace(unquote(password), "****"), "Send this exact message to the team chat.")
ok("Database login", f"PostGIS {version}, {count:,} detections in the table")

print("\nAll checks passed. Run the backend from the backend/ folder:  cd backend && python app.py\n"
      "then open http://127.0.0.1:5000/api/health/db")
