import csv
import io
from datetime import datetime, timedelta, timezone
from typing import List, Any
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from example_projects.pharmax.Backend.app.core.dependencies import require_role
from example_projects.pharmax.Backend.app.db.session import get_db
from example_projects.pharmax.Backend.app.models.audit_log_table import AuditLog
from example_projects.pharmax.Backend.app.models.user_table import User, UserRole
from example_projects.pharmax.Backend.app.models.product_unit_table import ProductUnit
from example_projects.pharmax.Backend.app.schemas.product_schema import CreateProduct, ReadProduct, UpdateProduct
from example_projects.pharmax.Backend.app.schemas.product_unit_schema import ReadProductUnit, UpdateProductUnit, CreateProductUnit
from example_projects.pharmax.Backend.app.models.stock_adjustment_table import StockAdjustment, StockAdjustmentStatus
from example_projects.pharmax.Backend.app.schemas.stock_adjustment_schema import (
    AdjustStockResponse,
    CreateStockAdjustment,
    ReadStockAdjustment,
    StockApprovalBypassGrantRead,
    StockApprovalBypassGrantRequest,
    StockApprovalBypassRevokeRequest,
    ReviewStockAdjustmentRequest,
    ReviewStockAdjustmentResponse,
)
from example_projects.pharmax.Backend.app.services.audit_service import AuditService
from example_projects.pharmax.Backend.app.services.product_service import ProductService
from example_projects.pharmax.Backend.app.models.invoice_item_table import InvoiceItem


router = APIRouter(prefix="/products", tags=["Products"])
GRANT_STOCK_BYPASS_ACTION = "GRANT_STOCK_ADJUSTMENT_AUTO_APPROVAL"
REVOKE_STOCK_BYPASS_ACTION = "REVOKE_STOCK_ADJUSTMENT_AUTO_APPROVAL"


# ================= CSV IMPORT =================

CSV_COLUMN_MAP = {
    "product name":                 "name",
    "name":                         "name",
    "brand name":                   "brand_name",
    "brand":                        "brand_name",
    "supplier":                     "supplier_name",
    "supplier name":                "supplier_name",
    "generic name":                 "generic_name",
    "generic":                      "generic_name",
    "stock threshold":              "reorder_level",
    "reorder level":                "reorder_level",
    "reorder":                      "reorder_level",
    "barcode":                      "barcode",
    "markup":                       "markup_percent",
    "markup %":                     "markup_percent",
    "markup_percent":               "markup_percent",
    "stock":                        "initial_quantity",
    "initial quantity":             "initial_quantity",
    "quantity":                     "initial_quantity",
    "type":                         "product_type",
    "product type":                 "product_type",
    "dispense without prescription":"dispense_without_prescription",
    "otc":                          "dispense_without_prescription",
    "item return policy":           "return_policy",
    "return policy":                "return_policy",
    "status":                       "status",
    "price":                        "price_per_unit",
    "price per unit":               "price_per_unit",
    "selling price":                "price_per_unit",
}


class ImportErrorRow(BaseModel):
    row: int
    name: str
    reason: str


class ImportResult(BaseModel):
    total: int
    created: int
    skipped: int
    errors: List[ImportErrorRow]


@router.post("/import", response_model=ImportResult)
async def import_products(
    file: UploadFile = File(...),
    skip_duplicates: bool = True,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")  # handles BOM from Excel-saved CSVs
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV has no header row")

    # Normalise headers via the column map
    header_map: dict[str, str] = {}
    for col in reader.fieldnames:
        mapped = CSV_COLUMN_MAP.get(col.strip().lower())
        if mapped:
            header_map[col] = mapped

    rows: list[dict] = []
    for raw_row in reader:
        mapped_row: dict[str, Any] = {}
        for orig_col, dest_col in header_map.items():
            mapped_row[dest_col] = raw_row.get(orig_col, "")
        rows.append(mapped_row)

    if not rows:
        raise HTTPException(status_code=400, detail="CSV contains no data rows")

    result = ProductService.bulk_import(
        db=db,
        rows=rows,
        user_id=current_user.id,
        skip_duplicates=skip_duplicates,
    )
    return result


# ================= CREATE =================

@router.post("/", response_model=ReadProduct, status_code=status.HTTP_201_CREATED)
def create_product(
    data: CreateProduct,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
) -> ReadProduct:
    try:
        return ProductService.create_product(
            db=db,
            data=data,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ================= LIST =================

def _get_selling_price(product) -> float:
    """Get selling_price from default product unit."""
    if product.product_units:
        for unit in product.product_units:
            if getattr(unit, 'is_default', False):
                return unit.price_per_unit
        return product.product_units[0].price_per_unit
    return 0.0


def _product_to_dict(product) -> dict:
    """Convert product to dict with selling_price."""
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "base_unit": product.base_unit,
        "brand_name": product.brand_name,
        "generic_name": product.generic_name,
        "supplier_name": product.supplier_name,
        "therapeutic_category": product.therapeutic_category,
        "barcode": product.barcode,
        "markup_percent": product.markup_percent,
        "reorder_level": product.reorder_level,
        "product_type": product.product_type,
        "dispense_without_prescription": product.dispense_without_prescription,
        "return_policy": product.return_policy,
        "status": product.status,
        "deleted_at": product.deleted_at,
        "quantity_on_hand": product.quantity_on_hand,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "product_units": product.product_units,
        "selling_price": _get_selling_price(product),
    }


def _as_local_naive(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone().replace(tzinfo=None)


def _now_local_naive() -> datetime:
    return _as_local_naive(datetime.now(timezone.utc)) or datetime.now()


def _parse_datetime_value(value) -> datetime | None:
    if isinstance(value, datetime):
        return _as_local_naive(value)
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return _as_local_naive(datetime.fromisoformat(text.replace("Z", "+00:00")))
    except ValueError:
        return None


def _collect_stock_bypass_grants(db: Session, *, target_user_id: str | None = None) -> dict[str, dict]:
    stmt = (
        select(AuditLog)
        .where(
            AuditLog.action.in_([GRANT_STOCK_BYPASS_ACTION, REVOKE_STOCK_BYPASS_ACTION]),
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

        if log.action == GRANT_STOCK_BYPASS_ACTION:
            user_id = str(details.get("target_user_id") or log.resource_id or "").strip()
            if not user_id:
                continue

            granted_at = _as_local_naive(log.created_at) or _now_local_naive()
            try:
                duration_minutes = int(details.get("duration_minutes") or 60)
            except (TypeError, ValueError):
                duration_minutes = 60
            duration_minutes = max(5, duration_minutes)
            expires_at = _parse_datetime_value(details.get("expires_at")) or (
                granted_at + timedelta(minutes=duration_minutes)
            )

            grants[grant_id] = {
                "grant_id": grant_id,
                "user_id": user_id,
                "granted_by_user_id": log.user_id,
                "duration_minutes": duration_minutes,
                "granted_at": granted_at,
                "expires_at": expires_at,
                "note": details.get("note"),
                "revoked_at": None,
            }
            continue

        existing = grants.get(grant_id)
        if existing is not None:
            existing["revoked_at"] = _as_local_naive(log.created_at)

    return grants


def _list_stock_bypass_permissions(
    db: Session,
    now_local: datetime,
    *,
    active_only: bool = True,
    target_user_id: str | None = None,
) -> list[dict]:
    grants = _collect_stock_bypass_grants(db, target_user_id=target_user_id)
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
        is_active = value.get("revoked_at") is None and value["expires_at"] > now_local
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
                "duration_minutes": value["duration_minutes"],
                "granted_at": value["granted_at"],
                "expires_at": value["expires_at"],
                "note": value.get("note"),
                "is_active": is_active,
            }
        )

    rows.sort(key=lambda row: row["expires_at"], reverse=False)
    return rows


def _active_stock_bypass_grant_for_user(db: Session, user_id: str, now_local: datetime) -> dict | None:
    rows = _list_stock_bypass_permissions(
        db,
        now_local,
        active_only=True,
        target_user_id=user_id,
    )
    if not rows:
        return None
    return rows[-1]


@router.get("/", response_model=List[ReadProduct])
def list_products(
    name: str | None = None,
    generic_name: str | None = None,
    therapeutic_category: str | None = None,
    min_stock: int | None = None,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    deleted: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)
    ),
):
    products = ProductService.list_products(
        db=db,
        name_filter=name,
        generic_name_filter=generic_name,
        therapeutic_category_filter=therapeutic_category,
        min_stock=min_stock,
        limit=limit,
        offset=offset,
        deleted=deleted,
    )
    # Convert to dict with selling_price
    return [_product_to_dict(p) for p in products]


# ================= READ =================

@router.get("/{product_id}", response_model=ReadProduct)
def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)
    ),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_to_dict(product)


# ================= UNITS =================

@router.get("/{product_id}/units", response_model=List[ReadProductUnit])
def get_product_units(
    product_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)
    ),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = select(ProductUnit).where(ProductUnit.product_id == product_id)
    return db.execute(stmt).scalars().all()


# ================= UNIT UPDATE =================

@router.post("/{product_id}/units", response_model=ReadProductUnit, status_code=status.HTTP_201_CREATED)
def add_product_unit(
    product_id: str,
    payload: CreateProductUnit,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    from example_projects.pharmax.Backend.app.services.product_unit_service import ProductUnitService
    try:
        return ProductUnitService.create_unit(
            db=db,
            product_id=product_id,
            name=payload.name,
            price_per_unit=payload.price_per_unit,
            multiplier_to_base=payload.multiplier_to_base,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{product_id}/units/{unit_id}", response_model=ReadProductUnit)
def update_product_unit(
    product_id: str,
    unit_id: str,
    payload: UpdateProductUnit,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    stmt = select(ProductUnit).where(
        ProductUnit.id == unit_id, ProductUnit.product_id == product_id
    )
    unit = db.execute(stmt).scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    for field, val in update_data.items():
        setattr(unit, field, val)
    db.commit()
    db.refresh(unit)
    return unit


# ================= STOCK =================

@router.get(
    "/stock-adjustments/approval-bypass-grants",
    response_model=List[StockApprovalBypassGrantRead],
)
def list_stock_approval_bypass_grants(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    now_local = _now_local_naive()
    return _list_stock_bypass_permissions(db, now_local, active_only=active_only)


@router.post(
    "/stock-adjustments/approval-bypass-grants",
    response_model=StockApprovalBypassGrantRead,
    status_code=status.HTTP_201_CREATED,
)
def grant_stock_approval_bypass(
    payload: StockApprovalBypassGrantRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    target_user = db.execute(select(User).where(User.id == payload.user_id)).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not target_user.is_active:
        raise HTTPException(status_code=400, detail="Only active users can receive temporary access")
    if target_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Admins already have direct stock adjustment access")

    now_local = _now_local_naive()
    expires_at = now_local + timedelta(minutes=payload.duration_minutes)
    grant_id = str(uuid4())

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action=GRANT_STOCK_BYPASS_ACTION,
        resource_type="USER",
        resource_id=target_user.id,
        details={
            "grant_id": grant_id,
            "target_user_id": target_user.id,
            "target_role": getattr(target_user.role, "value", target_user.role),
            "duration_minutes": payload.duration_minutes,
            "granted_at": now_local.isoformat(),
            "expires_at": expires_at.isoformat(),
            "note": payload.note,
        },
    )
    db.commit()

    grants = _list_stock_bypass_permissions(
        db,
        now_local,
        active_only=False,
        target_user_id=target_user.id,
    )
    for grant in reversed(grants):
        if grant["grant_id"] == grant_id:
            return grant

    return {
        "grant_id": grant_id,
        "user_id": target_user.id,
        "username": target_user.username,
        "full_name": target_user.full_name,
        "granted_by_user_id": current_user.id,
        "granted_by_name": current_user.full_name,
        "duration_minutes": payload.duration_minutes,
        "granted_at": now_local,
        "expires_at": expires_at,
        "note": payload.note,
        "is_active": True,
    }


@router.post(
    "/stock-adjustments/approval-bypass-grants/{grant_id}/revoke",
    response_model=StockApprovalBypassGrantRead,
)
def revoke_stock_approval_bypass(
    grant_id: str,
    payload: StockApprovalBypassRevokeRequest | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    now_local = _now_local_naive()
    grants = _list_stock_bypass_permissions(db, now_local, active_only=False)
    target = next((row for row in grants if row["grant_id"] == grant_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Temporary access grant not found")
    if not target["is_active"]:
        return target

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action=REVOKE_STOCK_BYPASS_ACTION,
        resource_type="USER",
        resource_id=target["user_id"],
        details={
            "grant_id": target["grant_id"],
            "target_user_id": target["user_id"],
            "revoked_at": now_local.isoformat(),
            "reason": payload.reason if payload else None,
        },
    )
    db.commit()

    refreshed = _list_stock_bypass_permissions(
        db,
        now_local,
        active_only=False,
        target_user_id=target["user_id"],
    )
    for grant in refreshed:
        if grant["grant_id"] == grant_id:
            return grant

    target["is_active"] = False
    return target


@router.get("/stock-adjustments/pending", response_model=List[ReadStockAdjustment])
def list_pending_stock_adjustments(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    stmt = (
        select(StockAdjustment)
        .where(StockAdjustment.status == StockAdjustmentStatus.PENDING)
        .order_by(StockAdjustment.created_at.asc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


@router.get("/{product_id}/adjustments", response_model=List[ReadStockAdjustment])
def get_stock_adjustments(
    product_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    stmt = (
        select(StockAdjustment)
        .where(StockAdjustment.product_id == product_id)
        .order_by(StockAdjustment.created_at.desc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


@router.post("/{product_id}/adjust-stock", response_model=AdjustStockResponse)
def adjust_stock(
    product_id: str,
    payload: CreateStockAdjustment,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        now_local = _now_local_naive()
        active_bypass = None
        if current_user.role in (UserRole.CASHIER, UserRole.STAFF):
            active_bypass = _active_stock_bypass_grant_for_user(db, current_user.id, now_local)

        requires_approval = current_user.role != UserRole.ADMIN and active_bypass is None
        approval_note = None
        if not requires_approval:
            if current_user.role == UserRole.ADMIN:
                approval_note = "Auto-approved by admin"
            elif active_bypass is not None:
                approval_note = (
                    "Auto-approved via temporary admin stock permission "
                    f"({active_bypass['grant_id']})"
                )

        adjustment = ProductService.adjust_stock(
            db=db,
            product=product,
            change_qty=payload.change_qty,
            reason=payload.reason.value,
            reference=payload.reference,
            note=payload.note,
            user_id=current_user.id,
            requires_approval=requires_approval,
            approval_note=approval_note,
        )
        db.refresh(product)
        return AdjustStockResponse(product=product, adjustment=adjustment)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{product_id}/adjustments/{adjustment_id}/review", response_model=ReviewStockAdjustmentResponse)
def review_stock_adjustment(
    product_id: str,
    adjustment_id: str,
    payload: ReviewStockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stmt = select(StockAdjustment).where(
        StockAdjustment.id == adjustment_id,
        StockAdjustment.product_id == product_id,
    )
    adjustment = db.execute(stmt).scalar_one_or_none()
    if not adjustment:
        raise HTTPException(status_code=404, detail="Adjustment not found")

    try:
        reviewed = ProductService.review_stock_adjustment(
            db=db,
            product=product,
            adjustment=adjustment,
            approve=payload.approve,
            reviewer_user_id=current_user.id,
            note=payload.note,
        )
        db.refresh(product)
        return ReviewStockAdjustmentResponse(product=product, adjustment=reviewed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ================= UPDATE =================

@router.patch("/{product_id}", response_model=ReadProduct)
def update_product(
    product_id: str,
    payload: UpdateProduct,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    return ProductService.update_product(
        db=db,
        product=product,
        updates=update_data,
        user_id=current_user.id,
    )


# ================= DELETE =================

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    db: Session = Depends(get_db),
    hard_delete: bool = False, 
    current_user=Depends(require_role(UserRole.ADMIN)),
):
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")


    stmt = select(InvoiceItem).where(InvoiceItem.product_id == product_id)
    if db.execute(stmt).scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Cannot delete product with invoice history",)

    if hard_delete:
        ProductService.hard_delete_product(db=db, product=product, user_id=current_user.id)
        return

    ProductService.soft_delete_product(db=db, product=product, user_id=current_user.id)
