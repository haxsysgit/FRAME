import os
from pathlib import Path

from dotenv import load_dotenv

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=False)

DB_DIR = BASE_DIR / "app" / "_db"
DB_PATH = DB_DIR / "pharmax.db"

# Production uses PHARMAX_DATABASE_URL or DATABASE_URL
# Development defaults to SQLite
_external_url = os.getenv("PHARMAX_DATABASE_URL") or os.getenv("DATABASE_URL")
if ENVIRONMENT == "production" and _external_url:
    # Render (and others) may set postgres:// but SQLAlchemy needs postgresql://
    DATABASE_URL = _external_url
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = f"sqlite:///{DB_PATH}"

IS_SQLITE = DATABASE_URL.startswith("sqlite")

SECRET_KEY = os.getenv("PHARMAX_SECRET_KEY", "pharmax-secret-change-me")
ALGORITHM = os.getenv("PHARMAX_JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("PHARMAX_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

_cors_origins_raw = os.getenv(
    "PHARMAX_CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:5174",
)
CORS_ORIGINS = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    text = str(raw).strip()
    if not text:
        return default
    try:
        return int(text, 0)
    except ValueError:
        return default


PRINTER_TYPE = os.getenv("PHARMAX_PRINTER_TYPE", os.getenv("PRINTER_TYPE", "network")).strip().lower()
USB_VENDOR_ID = _int_env("PHARMAX_USB_VENDOR_ID", _int_env("USB_VENDOR_ID", 0x04B8))
USB_PRODUCT_ID = _int_env("PHARMAX_USB_PRODUCT_ID", _int_env("USB_PRODUCT_ID", 0x0202))
PRINTER_IP = os.getenv("PHARMAX_PRINTER_IP", os.getenv("PRINTER_IP", "127.0.0.1")).strip()
PRINTER_PORT = _int_env("PHARMAX_PRINTER_PORT", _int_env("PRINTER_PORT", 9100))
