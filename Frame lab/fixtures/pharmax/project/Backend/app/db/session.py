import os

from sqlalchemy import create_engine, inspect, or_, select, text
from sqlalchemy.orm import sessionmaker

from example_projects.pharmax.Backend.app.core.config import DATABASE_URL, DB_DIR, ENVIRONMENT, IS_SQLITE
from example_projects.pharmax.Backend.app.core.security import get_password_hash, get_pin_hash
from example_projects.pharmax.Backend.app.db.base import Base
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole

if IS_SQLITE:
    DB_DIR.mkdir(parents=True, exist_ok=True)

engine_kwargs = {}
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    import example_projects.pharmax.Backend.app.models
    if ENVIRONMENT != "production":
        Base.metadata.create_all(bind=engine)
    _ensure_default_users_from_env()


def _ensure_default_users_from_env():
    if not inspect(engine).has_table("users"):
        return

    defaults = [
        {
            "username": os.getenv("PHARMAX_ADMIN_USERNAME", "admin"),
            "email": os.getenv("PHARMAX_ADMIN_EMAIL", "admin@pharmax.local"),
            "full_name": os.getenv("PHARMAX_ADMIN_FULL_NAME", "Admin"),
            "role": UserRole.ADMIN,
            "password": os.getenv("PHARMAX_ADMIN_PASSWORD"),
            "pin": None,
        },
        {
            "username": os.getenv("PHARMAX_CASHIER_USERNAME", "cashier"),
            "email": os.getenv("PHARMAX_CASHIER_EMAIL", "cashier@pharmax.local"),
            "full_name": os.getenv("PHARMAX_CASHIER_FULL_NAME", "Cashier"),
            "role": UserRole.CASHIER,
            "password": os.getenv("PHARMAX_CASHIER_PASSWORD"),
            "pin": os.getenv("PHARMAX_CASHIER_PIN", "0000"),
        },
        {
            "username": os.getenv("PHARMAX_STAFF_USERNAME", "staff"),
            "email": os.getenv("PHARMAX_STAFF_EMAIL", "staff@pharmax.local"),
            "full_name": os.getenv("PHARMAX_STAFF_FULL_NAME", "Staff"),
            "role": UserRole.STAFF,
            "password": os.getenv("PHARMAX_STAFF_PASSWORD"),
            "pin": os.getenv("PHARMAX_STAFF_PIN", "0000"),
        },
    ]

    db = SessionLocal()
    try:
        changed = False
        for item in defaults:
            password = item["password"]
            if not password:
                continue

            existing = db.execute(
                select(User).where(
                    or_(User.username == item["username"], User.email == item["email"])
                )
            ).scalar_one_or_none()

            if existing:
                if not existing.is_active:
                    existing.is_active = True
                    changed = True
                if item["pin"] and not existing.hashed_pin:
                    existing.hashed_pin = get_pin_hash(item["pin"])
                    changed = True
                continue

            user = User(
                username=item["username"],
                email=item["email"],
                full_name=item["full_name"],
                role=item["role"],
                hashed_password=get_password_hash(password),
                hashed_pin=get_pin_hash(item["pin"]) if item["pin"] else None,
                is_active=True,
            )
            db.add(user)
            changed = True

        if changed:
            db.commit()
    finally:
        db.close()
