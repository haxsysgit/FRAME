import argparse
import os
import sys
from pathlib import Path

from sqlalchemy import select

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from example_projects.pharmax.Backend.app.db.session import SessionLocal, init_db
from example_projects.pharmax.Backend.app.core.security import get_password_hash, get_pin_hash
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole


def _ensure_user(
    db,
    *,
    username: str,
    email: str,
    full_name: str,
    role: UserRole,
    password: str,
    pin: str | None = None,
) -> tuple[User, bool]:
    existing = db.execute(
        select(User).where((User.username == username) | (User.email == email))
    ).scalar_one_or_none()

    if existing:
        return existing, False

    created = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=get_password_hash(password),
        hashed_pin=get_pin_hash(pin) if pin else None,
        is_active=True,
    )
    db.add(created)
    db.commit()
    db.refresh(created)
    return created, True


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed default Pharmax users (ADMIN/CASHIER/STAFF).")

    parser.add_argument("--admin-username", default="admin")
    parser.add_argument("--admin-email", default="admin@pharmax.local")
    parser.add_argument("--admin-password", default=os.getenv("PHARMAX_ADMIN_PASSWORD"))

    parser.add_argument("--cashier-username", default="cashier")
    parser.add_argument("--cashier-email", default="cashier@pharmax.local")
    parser.add_argument("--cashier-password", default=os.getenv("PHARMAX_CASHIER_PASSWORD"))

    parser.add_argument("--staff-username", default="staff")
    parser.add_argument("--staff-email", default="staff@pharmax.local")
    parser.add_argument("--staff-password", default=os.getenv("PHARMAX_STAFF_PASSWORD"))

    parser.add_argument("--cashier-pin", default=os.getenv("PHARMAX_CASHIER_PIN", "1234"))
    parser.add_argument("--staff-pin", default=os.getenv("PHARMAX_STAFF_PIN", "5678"))

    args = parser.parse_args()

    missing = []
    if not args.admin_password:
        missing.append("--admin-password or PHARMAX_ADMIN_PASSWORD")
    if not args.cashier_password:
        missing.append("--cashier-password or PHARMAX_CASHIER_PASSWORD")
    if not args.staff_password:
        missing.append("--staff-password or PHARMAX_STAFF_PASSWORD")

    if missing:
        raise SystemExit(
            "Missing required passwords:\n- " + "\n- ".join(missing) + "\n\n"
            "Passwords must be at least 8 characters."
        )

    # Ensure tables and compatibility columns exist before ORM queries.
    # This prevents seed failures on older persisted schemas.
    init_db()

    db = SessionLocal()
    try:
        created_any = False

        _, created = _ensure_user(
            db,
            username=args.admin_username,
            email=args.admin_email,
            full_name="Admin",
            role=UserRole.ADMIN,
            password=args.admin_password,
        )
        created_any |= created
        print(f"{'CREATED' if created else 'EXISTS'} ADMIN: {args.admin_username} ({args.admin_email})")

        _, created = _ensure_user(
            db,
            username=args.cashier_username,
            email=args.cashier_email,
            full_name="Cashier",
            role=UserRole.CASHIER,
            password=args.cashier_password,
            pin=args.cashier_pin,
        )
        created_any |= created
        print(f"{'CREATED' if created else 'EXISTS'} CASHIER: {args.cashier_username} ({args.cashier_email})")

        _, created = _ensure_user(
            db,
            username=args.staff_username,
            email=args.staff_email,
            full_name="Staff",
            role=UserRole.STAFF,
            password=args.staff_password,
            pin=args.staff_pin,
        )
        created_any |= created
        print(f"{'CREATED' if created else 'EXISTS'} STAFF: {args.staff_username} ({args.staff_email})")

        if created_any:
            print("Seed complete.")
        else:
            print("No changes (all users already exist).")

    finally:
        db.close()


if __name__ == "__main__":
    main()
