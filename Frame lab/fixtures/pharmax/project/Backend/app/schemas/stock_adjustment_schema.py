from datetime import datetime

from pydantic import BaseModel, Field

from example_projects.pharmax.Backend.app.models.stock_adjustment_table import StockAdjustmentReason, StockAdjustmentStatus
from example_projects.pharmax.Backend.app.schemas.product_schema import ReadProduct


class StockAdjustmentBase(BaseModel):
    # Positive means stock increases; negative means stock decreases.
    change_qty: int

    # Why the stock changed (used for audit/reporting).
    reason: StockAdjustmentReason
    reference: str | None = None
    note: str | None = None


class CreateStockAdjustment(StockAdjustmentBase):
    pass

class ReadStockAdjustment(StockAdjustmentBase):
    model_config = {"from_attributes": True}
    id: str
    product_id: str
    status: StockAdjustmentStatus
    created_at: datetime
    created_by_user_id: str | None = None
    approved_by_user_id: str | None = None
    approved_at: datetime | None = None
    approval_note: str | None = None


class ReviewStockAdjustmentRequest(BaseModel):
    approve: bool
    note: str | None = None


class ReviewStockAdjustmentResponse(BaseModel):
    model_config = {"from_attributes": True}
    adjustment: ReadStockAdjustment
    product: ReadProduct


# Combined response schema for stock adjustments
class AdjustStockResponse(BaseModel):
    # Combined response: audit record + updated product snapshot (UI convenience).
    model_config = {"from_attributes": True}
    adjustment: ReadStockAdjustment
    product: ReadProduct


class StockApprovalBypassGrantRequest(BaseModel):
    user_id: str
    duration_minutes: int = Field(default=60, ge=5, le=720)
    note: str | None = Field(default=None, max_length=300)


class StockApprovalBypassRevokeRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=300)


class StockApprovalBypassGrantRead(BaseModel):
    grant_id: str
    user_id: str
    username: str | None = None
    full_name: str | None = None
    granted_by_user_id: str
    granted_by_name: str | None = None
    duration_minutes: int
    granted_at: datetime
    expires_at: datetime
    note: str | None = None
    is_active: bool
