from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.core.dependencies import require_role
from example_projects.pharmax.Backend.app.db.session import get_db
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole
from example_projects.pharmax.Backend.app.schemas.invoice_item_schema import AddInvoiceItem
from example_projects.pharmax.Backend.app.schemas.invoice_schema import (
    AfterHoursPermissionGrantRequest,
    AfterHoursPermissionRead,
    AfterHoursPermissionRevokeRequest,
    CancelInvoiceRequest,
    CreateInvoiceRequest,
    FinalizeInvoiceRequest,
    ManualReconciliationLockRequest,
    PrintReceiptResponseRead,
    ReadInvoice,
    ReconciliationRunSummaryRead,
    ReconciliationStatusRead,
    RunDailyReconciliationRequest,
    UpdateInvoiceNoteRequest,
)
from example_projects.pharmax.Backend.app.services.printing_service import PrintingService
from example_projects.pharmax.Backend.app.services.invoice_workflow_service import InvoiceWorkflowService


def _raise_http_for_workflow_error(exc: Exception) -> None:
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise exc


router = APIRouter()


@router.post("/", response_model=ReadInvoice)
def create_invoice(
    payload: CreateInvoiceRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF, UserRole.CASHIER)),
):
    try:
        invoice = InvoiceWorkflowService.create_invoice_for_user(
            db,
            current_user=current_user,
            cashier_note=(payload.cashier_note if payload else None),
        )
    except (PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.post("/{invoice_id}/items", response_model=ReadInvoice)
def add_invoice_item(
    invoice_id: str,
    item: AddInvoiceItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF, UserRole.CASHIER)),
):
    try:
        invoice = InvoiceWorkflowService.add_item_for_user(
            db,
            current_user=current_user,
            invoice_id=invoice_id,
            product_id=item.product_id,
            product_unit_id=item.product_unit_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.get("/all", response_model=list[ReadInvoice])
def list_invoices(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    try:
        parsed_status = InvoiceWorkflowService.parse_status_filter(status)
        invoices = InvoiceWorkflowService.list_invoices_for_user(
            db,
            current_user=current_user,
            status=parsed_status,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        _raise_http_for_workflow_error(exc)
    return [
        InvoiceWorkflowService.build_invoice_response(
            invoice, name=current_user.full_name
        )
        for invoice in invoices
    ]


@router.post("/{invoice_id}/finalize", response_model=ReadInvoice)
def finalize_invoice(
    invoice_id: str,
    body: FinalizeInvoiceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER)),
):
    try:
        invoice = InvoiceWorkflowService.finalize_invoice_for_user(
            db,
            current_user=current_user,
            invoice_id=invoice_id,
            payment_method=body.payment_method,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.post("/{invoice_id}/dispense", response_model=ReadInvoice)
def dispense_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
):
    try:
        invoice = InvoiceWorkflowService.dispense_invoice_for_user(
            db,
            current_user=current_user,
            invoice_id=invoice_id,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.post("/{invoice_id}/cancel", response_model=ReadInvoice)
def cancel_invoice(
    invoice_id: str,
    body: CancelInvoiceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    try:
        invoice = InvoiceWorkflowService.cancel_invoice_for_user(
            db,
            current_user=current_user,
            invoice_id=invoice_id,
            reason=(body.reason or "").strip() or None,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.post("/{invoice_id}/return", response_model=ReadInvoice)
def return_invoice_to_sender(
    invoice_id: str,
    body: CancelInvoiceRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER)),
):
    try:
        invoice = InvoiceWorkflowService.return_invoice_to_sender_for_user(
            db,
            current_user=current_user,
            invoice_id=invoice_id,
            reason=(body.reason if body else None),
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.post("/{invoice_id}/print-receipt", response_model=PrintReceiptResponseRead)
def print_invoice_receipt(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER)),
):
    try:
        invoice = InvoiceWorkflowService.read_invoice_or_raise(db, invoice_id=invoice_id)
    except LookupError as exc:
        _raise_http_for_workflow_error(exc)

    invoice_payload = InvoiceWorkflowService.build_invoice_response(
        invoice,
        name=current_user.full_name,
    ).model_dump(mode="json")
    return PrintingService.print_receipt(invoice=invoice_payload)


@router.get("/reconciliation/status", response_model=ReconciliationStatusRead)
def reconciliation_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    return InvoiceWorkflowService.reconciliation_status_for_user(db, current_user)


@router.post("/reconciliation/lock-day", response_model=ReconciliationStatusRead)
def lock_day_and_close_sales(
    body: ManualReconciliationLockRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return InvoiceWorkflowService.lock_day_and_close_sales(
        db,
        current_user=current_user,
        note=(body.note if body else None),
    )


@router.post("/reconciliation/run", response_model=ReconciliationRunSummaryRead)
def run_daily_reconciliation(
    body: RunDailyReconciliationRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return InvoiceWorkflowService.run_daily_reconciliation(
        db,
        current_user=current_user,
        note=(body.note if body else None),
    )


@router.get("/reconciliation/after-hours-grants", response_model=list[AfterHoursPermissionRead])
def list_after_hours_grants(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return InvoiceWorkflowService.list_after_hours_permissions(
        db,
        active_only=active_only,
    )


@router.post("/reconciliation/after-hours-grants", response_model=AfterHoursPermissionRead)
def grant_after_hours_access(
    payload: AfterHoursPermissionGrantRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return InvoiceWorkflowService.grant_after_hours_access(
            db,
            current_user=current_user,
            user_id=payload.user_id,
            duration_hours=payload.duration_hours,
            note=payload.note,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)


@router.post("/reconciliation/after-hours-grants/{grant_id}/revoke", response_model=AfterHoursPermissionRead)
def revoke_after_hours_access(
    grant_id: str,
    body: AfterHoursPermissionRevokeRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    try:
        return InvoiceWorkflowService.revoke_after_hours_access(
            db,
            current_user=current_user,
            grant_id=grant_id,
            reason=(body.reason if body else None),
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)


@router.get("/{invoice_id}", response_model=ReadInvoice)
def read_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    try:
        invoice = InvoiceWorkflowService.read_invoice_or_raise(db, invoice_id=invoice_id)
    except LookupError as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        invoice, name=current_user.full_name
    )


@router.patch("/{invoice_id}/cashier-note", response_model=ReadInvoice)
def update_invoice_cashier_note(
    invoice_id: str,
    body: UpdateInvoiceNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    try:
        updated = InvoiceWorkflowService.update_cashier_note_for_user(
            db,
            current_user=current_user,
            invoice_id=invoice_id,
            cashier_note=body.cashier_note,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        _raise_http_for_workflow_error(exc)
    return InvoiceWorkflowService.build_invoice_response(
        updated, name=current_user.full_name
    )
