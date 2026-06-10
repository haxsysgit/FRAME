from datetime import datetime

from pydantic import BaseModel, Field

from example_projects.pharmax.Backend.app.models.invoice_table import InvoiceStatus, PaymentMethod
from example_projects.pharmax.Backend.app.schemas.invoice_item_schema import ReadInvoiceItem


class CreateInvoiceRequest(BaseModel):
    cashier_note: str | None = Field(default=None, max_length=500)


class FinalizeInvoiceRequest(BaseModel):
    payment_method: PaymentMethod


class CancelInvoiceRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class UpdateInvoiceNoteRequest(BaseModel):
    cashier_note: str | None = Field(default=None, max_length=500)


class ManualReconciliationLockRequest(BaseModel):
    note: str | None = Field(default=None, max_length=300)


class RunDailyReconciliationRequest(BaseModel):
    note: str | None = Field(default=None, max_length=300)


class AfterHoursPermissionGrantRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=36)
    duration_hours: int = Field(default=1, ge=1, le=12)
    note: str | None = Field(default=None, max_length=300)


class AfterHoursPermissionRevokeRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class AfterHoursPermissionRead(BaseModel):
    grant_id: str
    user_id: str
    username: str | None = None
    full_name: str | None = None
    granted_by_user_id: str
    granted_by_name: str | None = None
    duration_hours: int
    granted_at: datetime
    expires_at: datetime
    note: str | None = None
    is_active: bool


class ReconciliationStatusRead(BaseModel):
    cutoff_hour: int
    lock_source: str
    lock_start_at: datetime
    is_locked_for_staff: bool
    has_after_hours_permission: bool
    permission_expires_at: datetime | None = None
    can_process_invoices_now: bool
    last_reconciliation_run_at: datetime | None = None
    reconciliation_needs_rerun: bool


class ReconciliationRunSummaryRead(BaseModel):
    for_date: str
    generated_at: datetime
    paid_revenue: float
    paid_invoice_count: int
    cash_total: float
    card_total: float
    bank_transfer_total: float
    draft_count: int
    stamped_count: int
    dispensed_count: int
    cancelled_count: int


class PrintReceiptResponseRead(BaseModel):
    success: bool
    message: str | None = None
    error: str | None = None
    receipt_text: str | None = None


class ReadInvoice(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    sold_by_id: str
    sold_by_name: str | None = None
    finalized_by_id: str | None = None
    dispensed_by_id: str | None = None
    name: str | None = None
    status: str
    payment_method: PaymentMethod | None = None
    total_amount: float | None = None
    cashier_note: str | None = None
    created_at: datetime
    finalized_at: datetime | None = None
    dispensed_at: datetime | None = None
    items: list[ReadInvoiceItem]
