import os
import sys
import time
import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from example_projects.pharmax.Backend.app.admin import setup_admin
from example_projects.pharmax.Backend.app.core.config import (
    BASE_DIR,
    CORS_ORIGINS,
    DATABASE_URL,
    SECRET_KEY,
)
from example_projects.pharmax.Backend.app.api.router import api_router
from example_projects.pharmax.Backend.app.db.session import init_db

_SERVER_START_TIME = time.time()


app = FastAPI(title="Pharmax Backend", version="1.0.0")


@app.get("/")
def get_root():
    return {
        "status": "success",
        "pharmacy": "Pharmax",
        "version": "1.0.0",
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
)

@app.on_event("startup")
def _startup():
    init_db()
    setup_admin(app, secret_key=SECRET_KEY)


app.include_router(api_router)


# ---------------------------------------------------------------------------
# TEMPORARY DEBUG ENDPOINT — no auth, returns system info for debugging
# ---------------------------------------------------------------------------
@app.get("/debug/status")
def debug_status():
    """Return debug info: Python version, DB path, env vars, .env contents, git hash."""
    # Read .env file directly
    env_path = BASE_DIR / ".env"
    env_file_contents = None
    if env_path.exists():
        try:
            env_file_contents = env_path.read_text()
        except Exception:
            env_file_contents = "<error reading .env>"
    else:
        env_file_contents = "<no .env file found>"

    # Git commit hash
    git_hash = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR),
            timeout=5,
        )
        if result.returncode == 0:
            git_hash = result.stdout.strip()
    except Exception:
        git_hash = "<git command failed>"

    uptime_seconds = round(time.time() - _SERVER_START_TIME, 2)

    return {
        "python_version": sys.version,
        "database_url": DATABASE_URL,
        "env_vars": dict(os.environ),
        "env_file_path": str(env_path),
        "env_file_contents": env_file_contents,
        "git_commit_hash": git_hash,
        "server_uptime_seconds": uptime_seconds,
    }
