from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.models.audit_log_table import AuditLog
from example_projects.pharmax.Backend.app.models.invoice_table import Invoice as InvoiceTable, InvoiceStatus, PaymentMethod
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole
from example_projects.pharmax.Backend.app.schemas.invoice_schema import ReadInvoice
from example_projects.pharmax.Backend.app.services.audit_service import AuditService
from example_projects.pharmax.Backend.app.services.invoice_service import DAILY_RECONCILIATION_CUTOFF_HOUR, InvoiceService


STATUS_DISPLAY_MAP = {
    "FINALIZED": "STAMPED",
}

MANUAL_DAILY_LOCK_ACTION = "MANUAL_DAILY_LOCK"
RUN_DAILY_RECONCILIATION_ACTION = "RUN_DAILY_RECONCILIATION"
GRANT_AFTER_HOURS_ACCESS_ACTION = "GRANT_AFTER_HOURS_INVOICE_ACCESS"
REVOKE_AFTER_HOURS_ACCESS_ACTION = "REVOKE_AFTER_HOURS_INVOICE_ACCESS"
LEGACY_GRANT_AFTER_HOURS_ACCESS_ACTION = "GRANT_AFTER_HOURS_ACCESS"
LEGACY_REVOKE_AFTER_HOURS_ACCESS_ACTION = "REVOKE_AFTER_HOURS_ACCESS"


class InvoiceWorkflowService:
    @staticmethod
    def display_status(value) -> str:
        raw = getattr(value, "value", value)
        normalized = str(raw or "").upper()
        return STATUS_DISPLAY_MAP.get(normalized, normalized)

    @staticmethod
    def parse_status_filter(value: str | None) -> InvoiceStatus | None:
        if not value:
            return None
        normalized = str(value).upper()
        if normalized == "STAMPED":
            normalized = "FINALIZED"
        try:
            return InvoiceStatus(normalized)
        except ValueError as exc:
            raise ValueError("Invalid invoice status filter") from exc

    @staticmethod
    def _as_local_naive(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value
        return value.astimezone().replace(tzinfo=None)

    @staticmethod
    def _now_local_naive() -> datetime:
        return InvoiceWorkflowService._as_local_naive(datetime.now(timezone.utc)) or datetime.now()

    @staticmethod
    def _day_bounds(now_local: datetime) -> tuple[datetime, datetime]:
        day_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        return day_start, day_start + timedelta(days=1)

    @staticmethod
    def _default_lock_start(now_local: datetime) -> datetime:
        return now_local.replace(
            hour=DAILY_RECONCILIATION_CUTOFF_HOUR,
            minute=0,
            second=0,
            microsecond=0,
        )

    @staticmethod
    def _parse_datetime_value(value) -> datetime | None:
        if isinstance(value, datetime):
            return InvoiceWorkflowService._as_local_naive(value)
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            return InvoiceWorkflowService._as_local_naive(
                datetime.fromisoformat(text.replace("Z", "+00:00"))
            )
        except ValueError:
            return None

    @staticmethod
    def _manual_lock_log_for_day(db: Session, now_local: datetime) -> AuditLog | None:
        day_start, day_end = InvoiceWorkflowService._day_bounds(now_local)
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.action == MANUAL_DAILY_LOCK_ACTION,
                AuditLog.resource_type == "SYSTEM",
                AuditLog.created_at >= day_start,
                AuditLog.created_at < day_end,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(1)
        )
        return db.execute(stmt).scalars().first()

    @staticmethod
    def _resolve_non_admin_lock_start(db: Session, now_local: datetime) -> tuple[datetime, str]:
        manual_log = InvoiceWorkflowService._manual_lock_log_for_day(db, now_local)
        if manual_log:
            manual_time = InvoiceWorkflowService._as_local_naive(manual_log.created_at)
            if manual_time:
                return manual_time, "manual"
        return InvoiceWorkflowService._default_lock_start(now_local), "automatic"

    @staticmethod
    def _collect_after_hours_grants(
        db: Session, *, target_user_id: str | None = None
    ) -> dict[str, dict]:
        grant_actions = {
            GRANT_AFTER_HOURS_ACCESS_ACTION,
            LEGACY_GRANT_AFTER_HOURS_ACCESS_ACTION,
        }
        revoke_actions = {
            REVOKE_AFTER_HOURS_ACCESS_ACTION,
            LEGACY_REVOKE_AFTER_HOURS_ACCESS_ACTION,
        }
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.action.in_(list(grant_actions | revoke_actions)),
                AuditLog.resource_type == "USER",
            )
            .order_by(AuditLog.created_at.asc())
        )
        if target_user_id:
            stmt = stmt.where(AuditLog.resource_id == target_user_id)

        logs = db.execute(stmt).scalars().all()
        grants: dict[str, dict] = {}

        for log in logs:
            details = log.details_dict
            grant_id = str(details.get("grant_id") or "").strip()
            if not grant_id:
                continue

            if log.action in grant_actions:
                user_id = str(details.get("target_user_id") or log.resource_id or "").strip()
                if not user_id:
                    continue

                granted_at = InvoiceWorkflowService._as_local_naive(log.created_at) or InvoiceWorkflowService._now_local_naive()
                try:
                    duration_hours = int(details.get("duration_hours") or 1)
                except (TypeError, ValueError):
                    duration_hours = 1
                expires_at = InvoiceWorkflowService._parse_datetime_value(details.get("expires_at")) or (
                    granted_at + timedelta(hours=max(1, duration_hours))
                )

                grants[grant_id] = {
                    "grant_id": grant_id,
                    "user_id": user_id,
                    "granted_by_user_id": log.user_id,
                    "duration_hours": max(1, duration_hours),
                    "granted_at": granted_at,
                    "expires_at": expires_at,
                    "note": details.get("note"),
                    "revoked_at": None,
                }
                continue

            existing = grants.get(grant_id)
            if existing is not None:
                existing["revoked_at"] = InvoiceWorkflowService._as_local_naive(log.created_at)

        return grants

    @staticmethod
    def list_after_hours_permissions(
        db: Session,
        *,
        active_only: bool = True,
        target_user_id: str | None = None,
        now_local: datetime | None = None,
    ) -> list[dict]:
        effective_now = now_local or InvoiceWorkflowService._now_local_naive()
        grants = InvoiceWorkflowService._collect_after_hours_grants(
            db, target_user_id=target_user_id
        )
        if not grants:
            return []

        user_ids: set[str] = set()
        for value in grants.values():
            if value.get("user_id"):
                user_ids.add(value["user_id"])
            if value.get("granted_by_user_id"):
                user_ids.add(value["granted_by_user_id"])

        user_lookup: dict[str, User] = {}
        if user_ids:
            users = db.execute(select(User).where(User.id.in_(user_ids))).scalars().all()
            user_lookup = {user.id: user for user in users}

        rows: list[dict] = []
        for value in grants.values():
            is_active = value.get("revoked_at") is None and value["expires_at"] > effective_now
            if active_only and not is_active:
                continue

            target_user = user_lookup.get(value["user_id"])
            grantor = user_lookup.get(value["granted_by_user_id"])
            rows.append(
                {
                    "grant_id": value["grant_id"],
                    "user_id": value["user_id"],
                    "username": target_user.username if target_user else None,
                    "full_name": target_user.full_name if target_user else None,
                    "granted_by_user_id": value["granted_by_user_id"],
                    "granted_by_name": grantor.full_name if grantor else None,
                    "duration_hours": value["duration_hours"],
                    "granted_at": value["granted_at"],
                    "expires_at": value["expires_at"],
                    "note": value.get("note"),
                    "is_active": is_active,
                }
            )

        rows.sort(key=lambda row: row["expires_at"], reverse=False)
        return rows

    @staticmethod
    def _active_after_hours_grant_for_user(
        db: Session, user_id: str, now_local: datetime
    ) -> dict | None:
        rows = InvoiceWorkflowService.list_after_hours_permissions(
            db,
            active_only=True,
            target_user_id=user_id,
            now_local=now_local,
        )
        if not rows:
            return None
        return rows[-1]

    @staticmethod
    def _latest_reconciliation_run_for_day(db: Session, now_local: datetime) -> AuditLog | None:
        day_start, day_end = InvoiceWorkflowService._day_bounds(now_local)
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.action == RUN_DAILY_RECONCILIATION_ACTION,
                AuditLog.resource_type == "SYSTEM",
                AuditLog.created_at >= day_start,
                AuditLog.created_at < day_end,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(1)
        )
        return db.execute(stmt).scalars().first()

    @staticmethod
    def _today_reconciliation_summary(db: Session, now_local: datetime) -> dict:
        day_start, day_end = InvoiceWorkflowService._day_bounds(now_local)
        invoices = db.execute(
            select(InvoiceTable).where(
                InvoiceTable.created_at >= day_start,
                InvoiceTable.created_at < day_end,
            )
        ).scalars().all()

        draft_count = 0
        stamped_count = 0
        dispensed_count = 0
        cancelled_count = 0
        paid_revenue = 0.0
        cash_total = 0.0
        card_total = 0.0
        bank_transfer_total = 0.0

        for invoice in invoices:
            status = str(getattr(invoice.status, "value", invoice.status) or "").upper()
            if status == "DRAFT":
                draft_count += 1
            elif status == "FINALIZED":
                stamped_count += 1
                amount = float(invoice.total_amount or 0)
                paid_revenue += amount
                method = str(getattr(invoice.payment_method, "value", invoice.payment_method) or "").upper()
                if method == "CASH":
                    cash_total += amount
                elif method == "POS":
                    card_total += amount
                elif method == "TRANSFER":
                    bank_transfer_total += amount
            elif status == "DISPENSED":
                dispensed_count += 1
                amount = float(invoice.total_amount or 0)
                paid_revenue += amount
                method = str(getattr(invoice.payment_method, "value", invoice.payment_method) or "").upper()
                if method == "CASH":
                    cash_total += amount
                elif method == "POS":
                    card_total += amount
                elif method == "TRANSFER":
                    bank_transfer_total += amount
            elif status == "CANCELLED":
                cancelled_count += 1

        return {
            "for_date": day_start.date().isoformat(),
            "generated_at": now_local,
            "paid_revenue": float(paid_revenue),
            "paid_invoice_count": stamped_count + dispensed_count,
            "cash_total": float(cash_total),
            "card_total": float(card_total),
            "bank_transfer_total": float(bank_transfer_total),
            "draft_count": draft_count,
            "stamped_count": stamped_count,
            "dispensed_count": dispensed_count,
            "cancelled_count": cancelled_count,
        }

    @staticmethod
    def _reconciliation_needs_rerun(
        db: Session,
        *,
        now_local: datetime,
        lock_start_at: datetime,
        last_reconciliation_run_at: datetime | None,
    ) -> bool:
        if now_local < lock_start_at:
            return False

        if last_reconciliation_run_at is None:
            summary = InvoiceWorkflowService._today_reconciliation_summary(db, now_local)
            return summary["stamped_count"] > 0 or summary["dispensed_count"] > 0

        day_start, day_end = InvoiceWorkflowService._day_bounds(now_local)
        count = (
            db.query(InvoiceTable.id)
            .filter(
                InvoiceTable.created_at >= day_start,
                InvoiceTable.created_at < day_end,
                InvoiceTable.status.in_([InvoiceStatus.FINALIZED, InvoiceStatus.DISPENSED]),
                or_(
                    and_(
                        InvoiceTable.finalized_at.isnot(None),
                        InvoiceTable.finalized_at > last_reconciliation_run_at,
                    ),
                    and_(
                        InvoiceTable.finalized_at.is_(None),
                        InvoiceTable.created_at > last_reconciliation_run_at,
                    ),
                ),
            )
            .count()
        )
        return count > 0

    @staticmethod
    def reconciliation_status_for_user(db: Session, current_user: User) -> dict:
        now_local = InvoiceWorkflowService._now_local_naive()
        lock_start_at, lock_source = InvoiceWorkflowService._resolve_non_admin_lock_start(
            db, now_local
        )
        is_locked_for_staff = now_local >= lock_start_at

        active_grant = None
        if current_user.role in {UserRole.CASHIER, UserRole.STAFF}:
            active_grant = InvoiceWorkflowService._active_after_hours_grant_for_user(
                db, current_user.id, now_local
            )

        has_after_hours_permission = active_grant is not None
        can_process_invoices_now = (
            current_user.role == UserRole.ADMIN
            or not is_locked_for_staff
            or has_after_hours_permission
        )

        latest_run_log = InvoiceWorkflowService._latest_reconciliation_run_for_day(db, now_local)
        last_run_at = (
            InvoiceWorkflowService._as_local_naive(latest_run_log.created_at)
            if latest_run_log
            else None
        )

        return {
            "cutoff_hour": DAILY_RECONCILIATION_CUTOFF_HOUR,
            "lock_source": lock_source,
            "lock_start_at": lock_start_at,
            "is_locked_for_staff": is_locked_for_staff,
            "has_after_hours_permission": has_after_hours_permission,
            "permission_expires_at": active_grant["expires_at"] if active_grant else None,
            "can_process_invoices_now": can_process_invoices_now,
            "last_reconciliation_run_at": last_run_at,
            "reconciliation_needs_rerun": InvoiceWorkflowService._reconciliation_needs_rerun(
                db,
                now_local=now_local,
                lock_start_at=lock_start_at,
                last_reconciliation_run_at=last_run_at,
            ),
        }

    @staticmethod
    def after_hours_forbidden_message(status_data: dict) -> str:
        lock_time = status_data["lock_start_at"].strftime("%I:%M %p").lstrip("0")
        return (
            f"Daily sales are closed after {lock_time}. "
            "Ask an admin to grant temporary after-hours access."
        )

    @staticmethod
    def _get_invoice_or_raise(db: Session, invoice_id: str) -> InvoiceTable:
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id)
        if not invoice:
            raise LookupError("Invoice not found")
        return invoice

    @staticmethod
    def _ensure_invoice_window_access(current_user: User, status_data: dict) -> None:
        if (
            current_user.role != UserRole.ADMIN
            and status_data["is_locked_for_staff"]
            and not status_data["has_after_hours_permission"]
        ):
            raise PermissionError(
                InvoiceWorkflowService.after_hours_forbidden_message(status_data)
            )

    @staticmethod
    def _handle_invoice_service_lock_error(exc: ValueError, *, status_data: dict) -> None:
        if "locked after daily reconciliation close" in str(exc):
            raise PermissionError(
                InvoiceWorkflowService.after_hours_forbidden_message(status_data)
            ) from exc
        raise exc

    @staticmethod
    def build_invoice_response(invoice: InvoiceTable, *, name: str | None = None) -> ReadInvoice:
        total = invoice.total_amount or (
            sum(float(item.quantity * item.unit_price) for item in invoice.items)
            if invoice.items
            else 0.0
        )
        sold_by_name = None
        if invoice.user:
            sold_by_name = (invoice.user.full_name or invoice.user.username or "").strip() or None
        return ReadInvoice(
            id=invoice.id,
            sold_by_id=invoice.sold_by_id,
            sold_by_name=sold_by_name,
            finalized_by_id=invoice.finalized_by_id,
            dispensed_by_id=invoice.dispensed_by_id,
            status=InvoiceWorkflowService.display_status(invoice.status),
            payment_method=invoice.payment_method,
            total_amount=total,
            cashier_note=invoice.cashier_note,
            created_at=invoice.created_at,
            finalized_at=invoice.finalized_at,
            dispensed_at=invoice.dispensed_at,
            items=invoice.items,
            name=name,
        )

    @staticmethod
    def create_invoice_for_user(
        db: Session,
        *,
        current_user: User,
        cashier_note: str | None = None,
    ) -> InvoiceTable:
        status_data = InvoiceWorkflowService.reconciliation_status_for_user(db, current_user)
        if not status_data["can_process_invoices_now"]:
            raise PermissionError(InvoiceWorkflowService.after_hours_forbidden_message(status_data))
        return InvoiceService.create_invoice(
            db=db,
            sold_by_id=current_user.id,
            cashier_note=cashier_note,
        )

    @staticmethod
    def add_item_for_user(
        db: Session,
        *,
        current_user: User,
        invoice_id: str,
        product_id: str,
        product_unit_id: str,
        quantity: int,
        unit_price,
    ) -> InvoiceTable:
        status_data = InvoiceWorkflowService.reconciliation_status_for_user(db, current_user)
        InvoiceWorkflowService._ensure_invoice_window_access(current_user, status_data)

        invoice = InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)
        requested_unit_price = unit_price if current_user.role == UserRole.ADMIN else None

        try:
            InvoiceService.add_item(
                db=db,
                invoice=invoice,
                product_id=product_id,
                product_unit_id=product_unit_id,
                quantity=quantity,
                unit_price=requested_unit_price,
                user_id=current_user.id,
                lock_cutoff_at=status_data["lock_start_at"],
                bypass_reconciliation_lock=(
                    current_user.role == UserRole.ADMIN
                    or status_data["has_after_hours_permission"]
                ),
            )
        except ValueError as exc:
            InvoiceWorkflowService._handle_invoice_service_lock_error(
                exc, status_data=status_data
            )

        db.refresh(invoice)
        return invoice

    @staticmethod
    def list_invoices_for_user(
        db: Session,
        *,
        current_user: User,
        status: InvoiceStatus | None,
        limit: int,
        offset: int,
    ) -> list[InvoiceTable]:
        return InvoiceService.list_invoices(
            db=db,
            status=status,
            user_id=current_user.id if current_user.role == UserRole.STAFF else None,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    def finalize_invoice_for_user(
        db: Session,
        *,
        current_user: User,
        invoice_id: str,
        payment_method: PaymentMethod,
    ) -> InvoiceTable:
        status_data = InvoiceWorkflowService.reconciliation_status_for_user(db, current_user)
        InvoiceWorkflowService._ensure_invoice_window_access(current_user, status_data)
        invoice = InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)

        try:
            InvoiceService.finalize_invoice(
                db,
                invoice,
                user_id=current_user.id,
                payment_method=payment_method,
                lock_cutoff_at=status_data["lock_start_at"],
                bypass_reconciliation_lock=(
                    current_user.role == UserRole.ADMIN
                    or status_data["has_after_hours_permission"]
                ),
            )
        except ValueError as exc:
            InvoiceWorkflowService._handle_invoice_service_lock_error(
                exc, status_data=status_data
            )

        db.refresh(invoice)
        return invoice

    @staticmethod
    def dispense_invoice_for_user(
        db: Session,
        *,
        current_user: User,
        invoice_id: str,
    ) -> InvoiceTable:
        invoice = InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)
        InvoiceService.dispense_invoice(db, invoice, user_id=current_user.id)
        db.refresh(invoice)
        return invoice

    @staticmethod
    def cancel_invoice_for_user(
        db: Session,
        *,
        current_user: User,
        invoice_id: str,
        reason: str | None = None,
    ) -> InvoiceTable:
        status_data = InvoiceWorkflowService.reconciliation_status_for_user(db, current_user)
        InvoiceWorkflowService._ensure_invoice_window_access(current_user, status_data)
        invoice = InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)

        if current_user.role == UserRole.STAFF and invoice.status != InvoiceStatus.DRAFT:
            raise PermissionError(
                "Staff can only cancel DRAFT invoices. Ask cashier/admin for stamped invoices."
            )

        try:
            InvoiceService.cancel_invoice(
                db,
                invoice,
                reason=reason,
                user_id=current_user.id,
                lock_cutoff_at=status_data["lock_start_at"],
                bypass_reconciliation_lock=(
                    current_user.role == UserRole.ADMIN
                    or status_data["has_after_hours_permission"]
                ),
            )
        except ValueError as exc:
            InvoiceWorkflowService._handle_invoice_service_lock_error(
                exc, status_data=status_data
            )

        db.refresh(invoice)
        return invoice

    @staticmethod
    def return_invoice_to_sender_for_user(
        db: Session,
        *,
        current_user: User,
        invoice_id: str,
        reason: str | None = None,
    ) -> InvoiceTable:
        if current_user.role not in {UserRole.ADMIN, UserRole.CASHIER}:
            raise PermissionError("Only admin or cashier can return invoices to the sender.")

        invoice = InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)
        InvoiceService.return_invoice_to_sender(
            db,
            invoice,
            user_id=current_user.id,
            reason=reason,
        )
        db.refresh(invoice)
        return invoice

    @staticmethod
    def read_invoice_or_raise(db: Session, *, invoice_id: str) -> InvoiceTable:
        return InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)

    @staticmethod
    def update_cashier_note_for_user(
        db: Session,
        *,
        current_user: User,
        invoice_id: str,
        cashier_note: str | None,
    ) -> InvoiceTable:
        invoice = InvoiceWorkflowService._get_invoice_or_raise(db, invoice_id)
        updated = InvoiceService.update_cashier_note(
            db,
            invoice,
            user_id=current_user.id,
            cashier_note=cashier_note,
        )
        return updated

    @staticmethod
    def lock_day_and_close_sales(
        db: Session,
        *,
        current_user: User,
        note: str | None = None,
    ) -> dict:
        now_local = InvoiceWorkflowService._now_local_naive()
        existing_lock = InvoiceWorkflowService._manual_lock_log_for_day(db, now_local)

        if not existing_lock:
            AuditService.log_action(
                db=db,
                user_id=current_user.id,
                action=MANUAL_DAILY_LOCK_ACTION,
                resource_type="SYSTEM",
                resource_id=now_local.date().isoformat(),
                details={
                    "locked_at": now_local.isoformat(),
                    "note": note,
                    "cutoff_hour": DAILY_RECONCILIATION_CUTOFF_HOUR,
                },
            )
            db.commit()

        return InvoiceWorkflowService.reconciliation_status_for_user(db, current_user)

    @staticmethod
    def run_daily_reconciliation(
        db: Session,
        *,
        current_user: User,
        note: str | None = None,
    ) -> dict:
        now_local = InvoiceWorkflowService._now_local_naive()
        
        # Auto-dispense all FINALIZED invoices for today
        day_start, day_end = InvoiceWorkflowService._day_bounds(now_local)
        finalized_invoices = db.execute(
            select(InvoiceTable).where(
                InvoiceTable.created_at >= day_start,
                InvoiceTable.created_at < day_end,
                InvoiceTable.status == InvoiceStatus.FINALIZED,
            )
        ).scalars().all()
        
        auto_dispensed_count = 0
        for invoice in finalized_invoices:
            invoice.status = InvoiceStatus.DISPENSED
            invoice.dispensed_by_id = current_user.id
            invoice.dispensed_at = datetime.now(timezone.utc)
            auto_dispensed_count += 1
        
        if auto_dispensed_count > 0:
            db.flush()
        
        summary = InvoiceWorkflowService._today_reconciliation_summary(db, now_local)
        summary["auto_dispensed_count"] = auto_dispensed_count

        AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action=RUN_DAILY_RECONCILIATION_ACTION,
            resource_type="SYSTEM",
            resource_id=summary["for_date"],
            details={
                **summary,
                "generated_at": summary["generated_at"].isoformat(),
                "note": note,
                "triggered_by": current_user.id,
            },
        )
        db.commit()

        return summary

    @staticmethod
    def grant_after_hours_access(
        db: Session,
        *,
        current_user: User,
        user_id: str,
        duration_hours: int,
        note: str | None = None,
    ) -> dict:
        target_user = db.execute(select(User).where(User.id == user_id)).scalars().first()
        if not target_user:
            raise LookupError("Selected user was not found.")
        if target_user.role not in {UserRole.CASHIER, UserRole.STAFF}:
            raise ValueError("Only cashier or staff accounts can receive after-hours access.")

        now_local = InvoiceWorkflowService._now_local_naive()
        grant_id = str(uuid4())
        expires_at = now_local + timedelta(hours=duration_hours)

        AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action=GRANT_AFTER_HOURS_ACCESS_ACTION,
            resource_type="USER",
            resource_id=target_user.id,
            details={
                "grant_id": grant_id,
                "target_user_id": target_user.id,
                "target_role": target_user.role.value,
                "duration_hours": duration_hours,
                "granted_at": now_local.isoformat(),
                "expires_at": expires_at.isoformat(),
                "note": note,
            },
        )
        db.commit()

        rows = InvoiceWorkflowService.list_after_hours_permissions(
            db,
            active_only=False,
            target_user_id=target_user.id,
            now_local=now_local,
        )
        created = next((row for row in rows if row["grant_id"] == grant_id), None)
        if created:
            return created

        return {
            "grant_id": grant_id,
            "user_id": target_user.id,
            "username": target_user.username,
            "full_name": target_user.full_name,
            "granted_by_user_id": current_user.id,
            "granted_by_name": current_user.full_name,
            "duration_hours": duration_hours,
            "granted_at": now_local,
            "expires_at": expires_at,
            "note": note,
            "is_active": True,
        }

    @staticmethod
    def revoke_after_hours_access(
        db: Session,
        *,
        current_user: User,
        grant_id: str,
        reason: str | None = None,
    ) -> dict:
        now_local = InvoiceWorkflowService._now_local_naive()
        rows = InvoiceWorkflowService.list_after_hours_permissions(
            db, active_only=False, now_local=now_local
        )
        target = next((row for row in rows if row["grant_id"] == grant_id), None)
        if not target:
            raise LookupError("Permission grant not found.")

        if not target["is_active"]:
            return target

        AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action=REVOKE_AFTER_HOURS_ACCESS_ACTION,
            resource_type="USER",
            resource_id=target["user_id"],
            details={
                "grant_id": grant_id,
                "target_user_id": target["user_id"],
                "revoked_at": now_local.isoformat(),
                "reason": reason,
            },
        )
        db.commit()

        refreshed_rows = InvoiceWorkflowService.list_after_hours_permissions(
            db, active_only=False, now_local=now_local
        )
        refreshed = next((row for row in refreshed_rows if row["grant_id"] == grant_id), None)
        if refreshed:
            return refreshed

        target["is_active"] = False
        return target
