#!/usr/bin/env python3
"""
Backend workflow smoke test (isolated DB, no running server required).

What this validates:
1. Create invoice + add item
2. Cashier draft listing shows invoice with items
3. Invoice detail includes items
4. Cancel draft invoice
5. Finalize and dispense invoice
6. Return draft invoice to sender
7. Core audit actions are recorded

Run:
  cd Backend
  uv run python scripts/smoke_test_workflows.py
"""

from __future__ import annotations

import argparse
import tempfile
import uuid
from pathlib import Path
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

import example_projects.pharmax.Backend.app.models  # noqa: F401  # register models for metadata
from example_projects.pharmax.Backend.app.core.security import get_password_hash, get_pin_hash
from example_projects.pharmax.Backend.app.db.base import Base
from example_projects.pharmax.Backend.app.models.audit_log_table import AuditLog
from example_projects.pharmax.Backend.app.models.invoice_table import InvoiceStatus, PaymentMethod
from example_projects.pharmax.Backend.app.models.product_table import Product, ProductStatus, ProductType
from example_projects.pharmax.Backend.app.models.product_unit_table import BaseUnit, ProductUnit
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole
from example_projects.pharmax.Backend.app.services.invoice_service import RETURNED_TO_SENDER_NOTE_PREFIX
from example_projects.pharmax.Backend.app.services.invoice_workflow_service import InvoiceWorkflowService


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def build_session_factory(db_path: Path) -> sessionmaker:
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def seed_users(db: Session) -> tuple[User, User, User]:
    admin = User(
        username="smoke_admin",
        email="smoke_admin@pharmax.local",
        full_name="Smoke Admin",
        role=UserRole.ADMIN,
        hashed_password=get_password_hash("SmokeAdmin123!"),
        is_active=True,
    )
    cashier = User(
        username="smoke_cashier",
        email="smoke_cashier@pharmax.local",
        full_name="Smoke Cashier",
        role=UserRole.CASHIER,
        hashed_password=get_password_hash("SmokeCashier123!"),
        hashed_pin=get_pin_hash("1234"),
        is_active=True,
    )
    staff = User(
        username="smoke_staff",
        email="smoke_staff@pharmax.local",
        full_name="Smoke Staff",
        role=UserRole.STAFF,
        hashed_password=get_password_hash("SmokeStaff123!"),
        hashed_pin=get_pin_hash("5678"),
        is_active=True,
    )
    db.add_all([admin, cashier, staff])
    db.commit()
    db.refresh(admin)
    db.refresh(cashier)
    db.refresh(staff)
    return admin, cashier, staff


def seed_product_and_unit(db: Session) -> tuple[Product, ProductUnit]:
    product = Product(
        sku=f"SMOKE-{uuid.uuid4().hex[:10].upper()}",
        name="Smoke Test Product",
        base_unit=BaseUnit.TABLET,
        brand_name="Smoke Brand",
        quantity_on_hand=500,
        reorder_level=10,
        product_type=ProductType.MEDICAL,
        dispense_without_prescription=True,
        status=ProductStatus.ACTIVE,
    )
    db.add(product)
    db.flush()

    unit = ProductUnit(
        product_id=product.id,
        name=BaseUnit.TABLET,
        multiplier_to_base=1,
        price_per_unit=150.0,
        is_default=True,
    )
    db.add(unit)
    db.commit()
    db.refresh(product)
    db.refresh(unit)
    return product, unit


def create_invoice_with_item(
    db: Session,
    *,
    actor: User,
    product: Product,
    unit: ProductUnit,
    quantity: int = 1,
) -> str:
    invoice = InvoiceWorkflowService.create_invoice_for_user(db, current_user=actor, cashier_note=None)
    updated = InvoiceWorkflowService.add_item_for_user(
        db,
        current_user=actor,
        invoice_id=invoice.id,
        product_id=product.id,
        product_unit_id=unit.id,
        quantity=quantity,
        unit_price=unit.price_per_unit,
    )
    ensure(len(updated.items or []) >= 1, "Add-item response returned invoice without items.")
    return invoice.id


def run_smoke(db: Session) -> None:
    admin, cashier, _ = seed_users(db)
    product, unit = seed_product_and_unit(db)

    print("1) create draft + add item ...", end=" ")
    draft_id = create_invoice_with_item(
        db,
        actor=admin,
        product=product,
        unit=unit,
        quantity=2,
    )
    print("OK")

    print("2) cashier list draft invoices includes items ...", end=" ")
    drafts = InvoiceWorkflowService.list_invoices_for_user(
        db,
        current_user=cashier,
        status=InvoiceWorkflowService.parse_status_filter("DRAFT"),
        limit=50,
        offset=0,
    )
    listed = next((inv for inv in drafts if inv.id == draft_id), None)
    ensure(listed is not None, "Draft invoice not found in cashier list.")
    ensure(len(listed.items or []) >= 1, "Cashier list returned draft invoice with zero items.")
    print("OK")

    print("3) invoice detail includes items ...", end=" ")
    draft_detail = InvoiceWorkflowService.read_invoice_or_raise(db, invoice_id=draft_id)
    ensure(len(draft_detail.items or []) >= 1, "Invoice detail returned zero items.")
    print("OK")

    print("4) cancel draft invoice ...", end=" ")
    cancelled = InvoiceWorkflowService.cancel_invoice_for_user(
        db,
        current_user=admin,
        invoice_id=draft_id,
        reason="Smoke test cancellation",
    )
    ensure(cancelled.status == InvoiceStatus.CANCELLED, "Cancel flow did not set CANCELLED status.")
    print("OK")

    print("5) finalize + dispense flow ...", end=" ")
    finalizable_id = create_invoice_with_item(
        db,
        actor=admin,
        product=product,
        unit=unit,
        quantity=1,
    )
    stamped = InvoiceWorkflowService.finalize_invoice_for_user(
        db,
        current_user=admin,
        invoice_id=finalizable_id,
        payment_method=PaymentMethod.CASH,
    )
    ensure(stamped.status == InvoiceStatus.FINALIZED, "Finalize flow did not set FINALIZED status.")
    dispensed = InvoiceWorkflowService.dispense_invoice_for_user(
        db,
        current_user=admin,
        invoice_id=finalizable_id,
    )
    ensure(dispensed.status == InvoiceStatus.DISPENSED, "Dispense flow did not set DISPENSED status.")
    print("OK")

    print("6) return-to-sender flow ...", end=" ")
    returnable_id = create_invoice_with_item(
        db,
        actor=admin,
        product=product,
        unit=unit,
        quantity=1,
    )
    returned = InvoiceWorkflowService.return_invoice_to_sender_for_user(
        db,
        current_user=admin,
        invoice_id=returnable_id,
        reason="Fix dosage",
    )
    ensure(returned.status == InvoiceStatus.DRAFT, "Returned invoice is no longer DRAFT.")
    ensure(
        str(returned.cashier_note or "").startswith(RETURNED_TO_SENDER_NOTE_PREFIX),
        "Returned invoice is missing return marker note.",
    )
    print("OK")

    print("7) audit actions are recorded ...", end=" ")
    actions = {
        row
        for row in db.execute(
            select(AuditLog.action).where(
                AuditLog.action.in_(
                    [
                        "SEND_TO_CASHIER_QUEUE",
                        "FINALIZE",
                        "DISPENSE",
                        "CANCEL",
                        "RETURN_TO_SENDER",
                    ]
                )
            )
        ).scalars()
    }
    expected = {"SEND_TO_CASHIER_QUEUE", "FINALIZE", "DISPENSE", "CANCEL", "RETURN_TO_SENDER"}
    missing = expected - actions
    ensure(not missing, f"Missing expected audit actions: {', '.join(sorted(missing))}")
    print("OK")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run isolated backend workflow smoke checks.")
    parser.add_argument(
        "--keep-db",
        action="store_true",
        help="Keep temporary DB file for debugging.",
    )
    args = parser.parse_args()

    tmp_dir = Path(tempfile.gettempdir()) / "pharmax-smoke"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    db_path = tmp_dir / f"workflow-smoke-{uuid.uuid4().hex}.db"

    session_factory = build_session_factory(db_path)
    db = session_factory()
    try:
        run_smoke(db)
        print(f"\n✅ Workflow smoke test passed (DB: {db_path})")
        return 0
    except Exception as exc:  # explicit failure path for CI/CLI use
        print(f"\n❌ Workflow smoke test failed: {exc}")
        print(f"DB path: {db_path}")
        return 1
    finally:
        db.close()
        if not args.keep_db:
            try:
                db_path.unlink(missing_ok=True)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
