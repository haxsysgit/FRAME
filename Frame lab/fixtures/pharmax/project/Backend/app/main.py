from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from example_projects.pharmax.Backend.app.admin import setup_admin
from example_projects.pharmax.Backend.app.core.config import CORS_ORIGINS, SECRET_KEY
from example_projects.pharmax.Backend.app.api.router import api_router
from example_projects.pharmax.Backend.app.db.session import init_db


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
