from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from datetime import datetime, timezone
from example_projects.pharmax.Backend.app.models.invoice_table import Invoice, InvoiceStatus, PaymentMethod
from example_projects.pharmax.Backend.app.models.invoice_item_table import InvoiceItem
from example_projects.pharmax.Backend.app.models.product_table import Product
from example_projects.pharmax.Backend.app.models.product_unit_table import ProductUnit
from example_projects.pharmax.Backend.app.services.audit_service import AuditService
from decimal import Decimal
from contextlib import contextmanager


DAILY_RECONCILIATION_CUTOFF_HOUR = 22
RETURNED_TO_SENDER_NOTE_PREFIX = "[RETURNED_TO_SENDER]"


class InvoiceService:

    @staticmethod
    def _as_local_naive(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone().replace(tzinfo=None)

    @staticmethod
    def _is_reconciliation_locked(
        invoice: Invoice,
        now: datetime | None = None,
        lock_cutoff_at: datetime | None = None,
    ) -> bool:
        created_at = InvoiceService._as_local_naive(invoice.created_at)
        if created_at is None:
            return False

        current_time = InvoiceService._as_local_naive(now or datetime.now(timezone.utc))
        if current_time is None:
            return False

        effective_cutoff = InvoiceService._as_local_naive(lock_cutoff_at)
        if effective_cutoff is None:
            effective_cutoff = current_time.replace(
                hour=DAILY_RECONCILIATION_CUTOFF_HOUR,
                minute=0,
                second=0,
                microsecond=0,
            )

        if created_at.date() < current_time.date():
            return True

        return created_at.date() == current_time.date() and current_time >= effective_cutoff

    @staticmethod
    def _enforce_reconciliation_lock(
        invoice: Invoice,
        *,
        bypass: bool = False,
        lock_cutoff_at: datetime | None = None,
    ) -> None:
        if bypass:
            return
        if InvoiceService._is_reconciliation_locked(invoice, lock_cutoff_at=lock_cutoff_at):
            raise ValueError("This invoice is locked after daily reconciliation close (10:00 PM).")

    @staticmethod
    @contextmanager
    def transaction(db: Session):
        try:
            yield
            db.commit()
        except Exception:
            db.rollback()
            raise

    # ================= CREATE =================

    @staticmethod
    def create_invoice(db: Session, sold_by_id: str, cashier_note: str | None = None) -> Invoice:
        with InvoiceService.transaction(db):
            invoice = Invoice(
                sold_by_id=sold_by_id,
                status=InvoiceStatus.DRAFT,
                cashier_note=(cashier_note or None),
            )

            db.add(invoice)

            AuditService.log_action(
                db=db,
                user_id=sold_by_id,
                action="CREATE",
                resource_type="INVOICE",
                resource_id=invoice.id,
                details={"created_by": sold_by_id, "has_cashier_note": bool(cashier_note)},
            )

        db.refresh(invoice)
        return invoice

    @staticmethod
    def update_cashier_note(
        db: Session,
        invoice: Invoice,
        *,
        user_id: str,
        cashier_note: str | None,
    ) -> Invoice:
        with InvoiceService.transaction(db):
            if invoice.status not in {InvoiceStatus.DRAFT, InvoiceStatus.FINALIZED}:
                raise ValueError("Only DRAFT or STAMPED invoices can be updated with cashier notes")

            normalized = (cashier_note or "").strip() or None
            invoice.cashier_note = normalized

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="UPDATE_NOTE",
                resource_type="INVOICE",
                resource_id=invoice.id,
                details={
                    "cashier_note": normalized,
                },
            )
        db.refresh(invoice)
        return invoice

    # ================= ADD ITEM =================

    @staticmethod
    def add_item(
        db: Session,
        invoice: Invoice,
        product_id: str,
        product_unit_id: str,
        quantity: int,
        unit_price: Decimal | None,
        user_id: str,
        *,
        lock_cutoff_at: datetime | None = None,
        bypass_reconciliation_lock: bool = False,
    ) -> InvoiceItem:

        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Can only add items to DRAFT invoices")

        InvoiceService._enforce_reconciliation_lock(
            invoice,
            bypass=bypass_reconciliation_lock,
            lock_cutoff_at=lock_cutoff_at,
        )

        stmt = select(Product).where(Product.id == product_id, Product.deleted_at.is_(None))
        product = db.execute(stmt).scalar_one_or_none()
        if not product:
            raise ValueError("Product not found")

        stmt = select(ProductUnit).where(ProductUnit.id == product_unit_id)
        unit = db.execute(stmt).scalar_one_or_none()
        if not unit or unit.product_id != product.id:
            raise ValueError("Invalid product unit")

        if unit_price is None:
            effective_unit_price = Decimal(str(unit.price_per_unit or 0))
        else:
            effective_unit_price = Decimal(str(unit_price))

        if effective_unit_price <= 0:
            raise ValueError("Unit price must be greater than zero")

        with InvoiceService.transaction(db):
            is_first_item = len(invoice.items or []) == 0
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=product_id,
                product_unit_id=product_unit_id,
                quantity=quantity,
                unit_price=effective_unit_price,
                line_total=float(quantity * effective_unit_price),
            )

            db.add(item)

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="ADD_ITEM",
                resource_type="INVOICE_ITEM",
                resource_id=item.id,
                details={
                    "invoice_id": invoice.id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": float(effective_unit_price),
                    "added_by": user_id,
                },
            )

            if is_first_item:
                AuditService.log_action(
                    db=db,
                    user_id=user_id,
                    action="SEND_TO_CASHIER_QUEUE",
                    resource_type="INVOICE",
                    resource_id=invoice.id,
                    details={
                        "invoice_id": invoice.id,
                        "sent_by": user_id,
                        "trigger": "first_item_added",
                    },
                )

        db.refresh(item)
        return item

    # ================= FINALIZE =================

    @staticmethod
    def finalize_invoice(
        db: Session,
        invoice: Invoice,
        user_id: str,
        payment_method: PaymentMethod,
        *,
        lock_cutoff_at: datetime | None = None,
        bypass_reconciliation_lock: bool = False,
    ) -> None:
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Only pending (DRAFT) invoices can be stamped")

        InvoiceService._enforce_reconciliation_lock(
            invoice,
            bypass=bypass_reconciliation_lock,
            lock_cutoff_at=lock_cutoff_at,
        )

        if not invoice.items:
            raise ValueError("Invoice has no items")

        with InvoiceService.transaction(db):
            total = Decimal("0.00")

            for item in invoice.items:
                unit = item.product_unit
                product = item.product

                base_qty = item.quantity * unit.multiplier_to_base
                if product.quantity_on_hand < base_qty:
                    raise ValueError(f"Insufficient stock for {product.name}")

                product.quantity_on_hand -= base_qty
                total += Decimal(str(item.quantity)) * Decimal(str(item.unit_price))

            invoice.status = InvoiceStatus.FINALIZED
            invoice.total_amount = total
            invoice.payment_method = payment_method
            invoice.finalized_by_id = user_id
            invoice.finalized_at = datetime.now(timezone.utc)

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="FINALIZE",
                resource_type="INVOICE",
                resource_id=invoice.id,
                details={
                    "total_amount": float(total),
                    "items_count": len(invoice.items),
                    "payment_method": payment_method.value,
                    "finalized_by": user_id,
                },
            )

    # ================= DISPENSE =================

    @staticmethod
    def dispense_invoice(db: Session, invoice: Invoice, user_id: str) -> None:
        if invoice.status != InvoiceStatus.FINALIZED:
            raise ValueError("Only STAMPED invoices can be dispensed")

        with InvoiceService.transaction(db):
            invoice.status = InvoiceStatus.DISPENSED
            invoice.dispensed_by_id = user_id
            invoice.dispensed_at = datetime.now(timezone.utc)

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="DISPENSE",
                resource_type="INVOICE",
                resource_id=invoice.id,
                details={
                    "dispensed_by": user_id,
                },
            )

    # ================= CANCEL =================

    @staticmethod
    def cancel_invoice(
        db: Session,
        invoice: Invoice,
        user_id: str,
        reason: str | None = None,
        *,
        lock_cutoff_at: datetime | None = None,
        bypass_reconciliation_lock: bool = False,
    ) -> None:

        if invoice.status == InvoiceStatus.CANCELLED:
            raise ValueError("Invoice already cancelled")

        if invoice.status == InvoiceStatus.DISPENSED:
            raise ValueError("Cannot cancel a dispensed invoice — goods already released")

        InvoiceService._enforce_reconciliation_lock(
            invoice,
            bypass=bypass_reconciliation_lock,
            lock_cutoff_at=lock_cutoff_at,
        )

        with InvoiceService.transaction(db):
            if invoice.status == InvoiceStatus.FINALIZED:
                for item in invoice.items:
                    base_qty = (
                        item.quantity * item.product_unit.multiplier_to_base
                    )
                    item.product.quantity_on_hand += base_qty

            invoice.status = InvoiceStatus.CANCELLED

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="CANCEL",
                resource_type="INVOICE",
                resource_id=invoice.id,
                details={
                    "reason": reason,
                    "cancelled_by": user_id,
                },
            )

    @staticmethod
    def return_invoice_to_sender(
        db: Session,
        invoice: Invoice,
        *,
        user_id: str,
        reason: str | None = None,
    ) -> None:
        if invoice.status != InvoiceStatus.DRAFT:
            raise ValueError("Only DRAFT invoices can be returned to the sender")

        normalized_reason = (reason or "").strip()
        return_note = RETURNED_TO_SENDER_NOTE_PREFIX
        if normalized_reason:
            return_note = f"{return_note} {normalized_reason}"

        with InvoiceService.transaction(db):
            invoice.cashier_note = return_note

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="RETURN_TO_SENDER",
                resource_type="INVOICE",
                resource_id=invoice.id,
                details={
                    "invoice_id": invoice.id,
                    "returned_to_user_id": invoice.sold_by_id,
                    "reason": normalized_reason or None,
                },
            )

    @staticmethod
    def list_invoices(
        db: Session, 
        user_id: str | None, 
        status: InvoiceStatus | None = InvoiceStatus.FINALIZED,
        limit: int = 50,
        offset: int = 0
    ) -> list[Invoice]:
        stmt = select(Invoice).options(selectinload(Invoice.user))
        if user_id:
            stmt = stmt.where(Invoice.sold_by_id == user_id)
        
        if status:
            stmt = stmt.where(Invoice.status == status)
        
        stmt = stmt.order_by(Invoice.created_at.desc()).offset(offset).limit(limit)
        invoices = db.execute(stmt).scalars().unique().all()

        if user_id:
            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="LIST",
                resource_type="INVOICE",
                resource_id=None,
                details={
                    "status": status.value if status else None,
                    "limit": limit,
                    "offset": offset,
                    "results_count": len(invoices),
                    "filtered_by_user": user_id is not None,
                },
            )
        
        return invoices

    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: str) -> Invoice | None:
        """Get invoice by ID with relationships loaded."""
        stmt = select(Invoice).options(
            selectinload(Invoice.user),
            selectinload(Invoice.items).selectinload(InvoiceItem.product),
            selectinload(Invoice.items).selectinload(InvoiceItem.product_unit)
        ).where(Invoice.id == invoice_id)
        return db.execute(stmt).scalar_one_or_none()


                    
