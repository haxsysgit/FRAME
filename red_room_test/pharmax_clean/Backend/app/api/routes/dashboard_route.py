"""
Dashboard metrics endpoint — returns aggregated data for fast loading.
"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from typing import Literal

from example_projects.pharmax.Backend.app.core.dependencies import require_role
from example_projects.pharmax.Backend.app.db.session import get_db
from example_projects.pharmax.Backend.app.models import (
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Product,
    ProductStatus,
    StockAdjustment,
    StockAdjustmentStatus,
    User,
    UserRole,
)


PAID_STATUSES = (InvoiceStatus.FINALIZED, InvoiceStatus.DISPENSED)
STATUS_DISPLAY_MAP = {
    "FINALIZED": "STAMPED",
}


def _base_invoice_query(db: Session, current_user: User, sold_by_id: str | None = None):
    query = db.query(Invoice)
    if current_user.role == UserRole.STAFF:
        if sold_by_id and sold_by_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not allowed to request reports for another staff user")
        query = query.filter(Invoice.sold_by_id == current_user.id)
    elif sold_by_id:
        query = query.filter(Invoice.sold_by_id == sold_by_id)
    return query


def _is_paid_status(status) -> bool:
    value = getattr(status, "value", status)
    normalized = str(value or "").upper()
    return normalized in {"FINALIZED", "STAMPED", "DISPENSED"}


def _display_status(value) -> str:
    raw = getattr(value, "value", value)
    normalized = str(raw or "").upper()
    return STATUS_DISPLAY_MAP.get(normalized, normalized)


def _as_payment_method(value) -> str:
    if value is None:
        return "UNKNOWN"
    raw = getattr(value, "value", value)
    normalized = str(raw).upper()
    return "TRANSFER" if normalized == "BANK_TRANSFER" else normalized


def _percent_change(current: float, previous: float) -> float:
    current_value = float(current or 0)
    previous_value = float(previous or 0)
    if previous_value == 0:
        return 0.0 if current_value == 0 else 100.0
    return round(((current_value - previous_value) / previous_value) * 100, 2)


def _trend_bucket_start(day_value: date, granularity: str) -> date:
    if granularity == "week":
        return day_value - timedelta(days=day_value.weekday())
    if granularity == "month":
        return day_value.replace(day=1)
    return day_value


def _build_revenue_trend(trend_map: dict[str, dict], range_start: date, range_days: int, granularity: str):
    if granularity == "day":
        revenue_trend = []
        for i in range(range_days):
            current_day = range_start + timedelta(days=i)
            key = current_day.isoformat()
            revenue_trend.append(trend_map.get(key, {"day": key, "revenue": 0.0, "invoice_count": 0}))
        return revenue_trend

    buckets = {}
    for i in range(range_days):
        current_day = range_start + timedelta(days=i)
        key = current_day.isoformat()
        row = trend_map.get(key, {"revenue": 0.0, "invoice_count": 0})
        bucket_key = _trend_bucket_start(current_day, granularity).isoformat()
        if bucket_key not in buckets:
            buckets[bucket_key] = {
                "day": bucket_key,
                "revenue": 0.0,
                "invoice_count": 0,
            }
        buckets[bucket_key]["revenue"] += float(row.get("revenue") or 0)
        buckets[bucket_key]["invoice_count"] += int(row.get("invoice_count") or 0)

    return [buckets[key] for key in sorted(buckets.keys())]


def _top_product_in_window(
    db: Session,
    current_user: User,
    start_at: datetime,
    sold_by_id: str | None = None,
    end_at: datetime | None = None,
):
    query = (
        db.query(
            InvoiceItem.product_id.label("product_id"),
            Product.name.label("product_name"),
            func.sum(InvoiceItem.quantity).label("quantity"),
            func.coalesce(func.sum(InvoiceItem.line_total), 0.0).label("revenue"),
        )
        .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
        .join(Product, InvoiceItem.product_id == Product.id)
        .filter(
            Invoice.created_at >= start_at,
            Invoice.status.in_(PAID_STATUSES),
        )
    )

    if end_at is not None:
        query = query.filter(Invoice.created_at < end_at)

    if current_user.role == UserRole.STAFF:
        query = query.filter(Invoice.sold_by_id == current_user.id)
    elif sold_by_id:
        query = query.filter(Invoice.sold_by_id == sold_by_id)

    row = query.group_by(InvoiceItem.product_id, Product.name).order_by(desc("quantity")).first()
    if not row:
        return None

    return {
        "product_id": str(row.product_id),
        "product_name": row.product_name,
        "quantity": int(row.quantity or 0),
        "revenue": float(row.revenue or 0),
    }

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    """
    Returns pre-aggregated dashboard metrics for fast loading.
    """
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    invoice_query = _base_invoice_query(db, current_user)

    # Today's invoices count and revenue
    today_invoices = (
        invoice_query
        .filter(Invoice.created_at >= today_start, Invoice.created_at <= today_end)
        .all()
    )

    today_revenue = sum(
        inv.total_amount or 0
        for inv in today_invoices
        if _is_paid_status(inv.status)
    )

    # Active products count
    active_products = db.query(func.count(Product.id)).filter(
        Product.status == ProductStatus.ACTIVE
    ).scalar() or 0

    out_of_stock_count = db.query(func.count(Product.id)).filter(
        Product.status == ProductStatus.ACTIVE,
        Product.quantity_on_hand <= 0,
    ).scalar() or 0

    # Low stock items (limit 10 for dashboard)
    low_stock_items = db.query(Product).filter(
        Product.status == ProductStatus.ACTIVE,
        Product.reorder_level > 0,
        Product.quantity_on_hand <= Product.reorder_level,
    ).limit(10).all()

    # Credit outstanding
    paid_invoices_for_credit = (
        invoice_query
        .filter(Invoice.status.in_(PAID_STATUSES))
        .all()
    )
    credit_outstanding = sum(
        inv.total_amount or 0
        for inv in paid_invoices_for_credit
        if _as_payment_method(inv.payment_method) == "CREDIT"
    )

    # Recent invoices (last 8)
    recent_invoices = invoice_query.order_by(
        Invoice.created_at.desc()
    ).limit(8).all()

    # Total invoices count
    total_invoices = invoice_query.with_entities(func.count(Invoice.id)).scalar() or 0

    cancelled_invoice_count_today = (
        invoice_query
        .filter(
            Invoice.created_at >= today_start,
            Invoice.created_at <= today_end,
            Invoice.status == InvoiceStatus.CANCELLED,
        )
        .with_entities(func.count(Invoice.id))
        .scalar()
        or 0
    )

    pending_user_approvals = 0
    pending_stock_adjustments = 0
    if current_user.role == UserRole.ADMIN:
        pending_user_approvals = (
            db.query(func.count(User.id))
            .filter(User.is_active.is_(False), User.last_login_at.is_(None))
            .scalar()
            or 0
        )
        pending_stock_adjustments = (
            db.query(func.count(StockAdjustment.id))
            .filter(StockAdjustment.status == StockAdjustmentStatus.PENDING)
            .scalar()
            or 0
        )

    return {
        "today_invoice_count": len(today_invoices),
        "today_revenue": today_revenue,
        "active_products": active_products,
        "out_of_stock_count": out_of_stock_count,
        "low_stock_items": [
            {
                "id": str(p.id),
                "name": p.name,
                "quantity_on_hand": p.quantity_on_hand,
                "reorder_level": p.reorder_level,
            }
            for p in low_stock_items
        ],
        "credit_outstanding": credit_outstanding,
        "recent_invoices": [
            {
                "id": str(inv.id),
                "name": f"INV-{str(inv.id)[:8]}",
                "status": _display_status(inv.status),
                "total_amount": inv.total_amount,
                "payment_method": _as_payment_method(inv.payment_method),
                "sold_by_id": str(inv.sold_by_id) if inv.sold_by_id else None,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
            for inv in recent_invoices
        ],
        "total_invoices": total_invoices,
        "cancelled_invoice_count_today": cancelled_invoice_count_today,
        "pending_user_approvals": pending_user_approvals,
        "pending_stock_adjustments": pending_stock_adjustments,
        "scope": "self" if current_user.role == UserRole.STAFF else "global",
    }


@router.get("/analytics")
def get_dashboard_analytics(
    range_days: int = Query(default=30, ge=1, le=365),
    as_of_date: date | None = Query(default=None),
    trend_granularity: Literal["day", "week", "month"] = Query(default="day"),
    top_n: int = Query(default=10, ge=1, le=25),
    staff_limit: int = Query(default=5, ge=1, le=20),
    invoice_limit: int = Query(default=5, ge=1, le=20),
    include_context: bool = Query(default=True),
    sold_by_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER, UserRole.STAFF)),
):
    report_day = as_of_date or date.today()
    today = report_day
    today_start = datetime.combine(today, datetime.min.time())
    week_start = today_start - timedelta(days=6)
    range_start = today_start - timedelta(days=range_days - 1)
    range_end = today_start + timedelta(days=1)

    invoice_query = _base_invoice_query(db, current_user, sold_by_id=sold_by_id)
    seller_scope_id = current_user.id if current_user.role == UserRole.STAFF else sold_by_id

    paid_invoice_query = invoice_query.filter(
        Invoice.created_at >= range_start,
        Invoice.created_at < range_end,
        Invoice.status.in_(PAID_STATUSES),
    )
    paid_invoices = paid_invoice_query.all()

    range_invoice_count = (
        invoice_query
        .filter(Invoice.created_at >= range_start, Invoice.created_at < range_end)
        .with_entities(func.count(Invoice.id))
        .scalar()
        or 0
    )

    paid_invoice_count = len(paid_invoices)
    total_revenue = float(sum(inv.total_amount or 0 for inv in paid_invoices))
    average_ticket = total_revenue / paid_invoice_count if paid_invoice_count else 0.0

    highest_invoice = (
        paid_invoice_query
        .order_by(desc(Invoice.total_amount), desc(Invoice.created_at))
        .first()
    )

    payment_mix_query = (
        db.query(
            Invoice.payment_method.label("method"),
            func.count(Invoice.id).label("invoice_count"),
            func.coalesce(func.sum(Invoice.total_amount), 0.0).label("revenue"),
        )
        .filter(
            Invoice.created_at >= range_start,
            Invoice.created_at < range_end,
            Invoice.status.in_(PAID_STATUSES),
        )
    )
    if seller_scope_id:
        payment_mix_query = payment_mix_query.filter(Invoice.sold_by_id == seller_scope_id)
    payment_mix_rows = payment_mix_query.group_by(Invoice.payment_method).order_by(desc("revenue")).all()

    status_rows = (
        invoice_query
        .filter(Invoice.created_at >= range_start, Invoice.created_at < range_end)
        .with_entities(Invoice.status.label("status"), func.count(Invoice.id).label("count"))
        .group_by(Invoice.status)
        .all()
    )
    status_counts = {
        "DRAFT": 0,
        "STAMPED": 0,
        "DISPENSED": 0,
        "CANCELLED": 0,
    }
    for row in status_rows:
        key = _display_status(row.status)
        if key in status_counts:
            status_counts[key] = int(row.count or 0)

    trend_query = (
        db.query(
            func.date(Invoice.created_at).label("day"),
            func.coalesce(func.sum(Invoice.total_amount), 0.0).label("revenue"),
            func.count(Invoice.id).label("invoice_count"),
        )
        .filter(
            Invoice.created_at >= range_start,
            Invoice.created_at < range_end,
            Invoice.status.in_(PAID_STATUSES),
        )
    )
    if seller_scope_id:
        trend_query = trend_query.filter(Invoice.sold_by_id == seller_scope_id)
    trend_rows = trend_query.group_by(func.date(Invoice.created_at)).order_by(func.date(Invoice.created_at)).all()
    trend_map = {
        str(row.day): {
            "day": str(row.day),
            "revenue": float(row.revenue or 0),
            "invoice_count": int(row.invoice_count or 0),
        }
        for row in trend_rows
    }
    revenue_trend = _build_revenue_trend(
        trend_map=trend_map,
        range_start=range_start.date(),
        range_days=range_days,
        granularity=trend_granularity,
    )

    top_products_query = (
        db.query(
            InvoiceItem.product_id.label("product_id"),
            Product.name.label("product_name"),
            func.sum(InvoiceItem.quantity).label("quantity"),
            func.coalesce(func.sum(InvoiceItem.line_total), 0.0).label("revenue"),
        )
        .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
        .join(Product, InvoiceItem.product_id == Product.id)
        .filter(
            Invoice.created_at >= range_start,
            Invoice.created_at < range_end,
            Invoice.status.in_(PAID_STATUSES),
        )
    )
    if seller_scope_id:
        top_products_query = top_products_query.filter(Invoice.sold_by_id == seller_scope_id)
    top_products_rows = (
        top_products_query
        .group_by(InvoiceItem.product_id, Product.name)
        .order_by(desc("quantity"), desc("revenue"))
        .limit(top_n)
        .all()
    )

    top_staff_query = (
        db.query(
            User.id.label("user_id"),
            User.full_name.label("full_name"),
            User.username.label("username"),
            func.count(Invoice.id).label("invoice_count"),
            func.coalesce(func.sum(Invoice.total_amount), 0.0).label("revenue"),
        )
        .join(Invoice, Invoice.sold_by_id == User.id)
        .filter(
            Invoice.created_at >= range_start,
            Invoice.created_at < range_end,
            Invoice.status.in_(PAID_STATUSES),
        )
    )
    if seller_scope_id:
        top_staff_query = top_staff_query.filter(User.id == seller_scope_id)
    top_staff_rows = (
        top_staff_query
        .group_by(User.id, User.full_name, User.username)
        .order_by(desc("revenue"))
        .limit(staff_limit)
        .all()
    )

    top_invoices_query = invoice_query.filter(
        Invoice.created_at >= range_start,
        Invoice.created_at < range_end,
        Invoice.status.in_(PAID_STATUSES),
    )
    top_invoices = (
        top_invoices_query
        .order_by(desc(Invoice.total_amount), desc(Invoice.created_at))
        .limit(invoice_limit)
        .all()
    )

    most_common_today = _top_product_in_window(
        db,
        current_user,
        today_start,
        sold_by_id=seller_scope_id,
        end_at=range_end,
    )
    most_common_week = _top_product_in_window(
        db,
        current_user,
        week_start,
        sold_by_id=seller_scope_id,
        end_at=range_end,
    )

    top_products = [
        {
            "product_id": str(row.product_id),
            "product_name": row.product_name,
            "quantity": int(row.quantity or 0),
            "revenue": float(row.revenue or 0),
        }
        for row in top_products_rows
    ]

    top_staff = [
        {
            "user_id": str(row.user_id),
            "name": row.full_name or row.username or "Unknown",
            "invoice_count": int(row.invoice_count or 0),
            "revenue": float(row.revenue or 0),
        }
        for row in top_staff_rows
    ]

    payment_total = sum(float(row.revenue or 0) for row in payment_mix_rows)
    payment_mix = [
        {
            "method": _as_payment_method(row.method),
            "invoice_count": int(row.invoice_count or 0),
            "revenue": float(row.revenue or 0),
            "percent": round(((float(row.revenue or 0) / payment_total) * 100), 2) if payment_total else 0,
        }
        for row in payment_mix_rows
    ]

    status_mix = []
    status_total = sum(status_counts.values())
    for key in ("DRAFT", "STAMPED", "DISPENSED", "CANCELLED"):
        count = status_counts[key]
        status_mix.append(
            {
                "status": key,
                "count": count,
                "percent": round((count / status_total) * 100, 2) if status_total else 0,
            }
        )

    kpis = {
        "total_revenue": total_revenue,
        "paid_invoice_count": paid_invoice_count,
        "invoice_count": int(range_invoice_count),
        "average_ticket": average_ticket,
        "highest_invoice": {
            "id": str(highest_invoice.id),
            "name": f"INV-{str(highest_invoice.id)[:8]}",
            "amount": float(highest_invoice.total_amount or 0),
            "status": _display_status(highest_invoice.status),
            "created_at": highest_invoice.created_at.isoformat() if highest_invoice.created_at else None,
            "sold_by_id": str(highest_invoice.sold_by_id) if highest_invoice.sold_by_id else None,
        } if highest_invoice else None,
        "best_selling_product": top_products[0] if top_products else None,
        "top_staff": top_staff[0] if top_staff else None,
        "most_common_product_today": most_common_today,
        "most_common_product_week": most_common_week,
    }

    if include_context:
        previous_range_start = range_start - timedelta(days=range_days)
        previous_paid_invoices = (
            invoice_query
            .filter(
                Invoice.created_at >= previous_range_start,
                Invoice.created_at < range_start,
                Invoice.status.in_(PAID_STATUSES),
            )
            .all()
        )
        previous_total_revenue = float(sum(inv.total_amount or 0 for inv in previous_paid_invoices))
        previous_paid_invoice_count = len(previous_paid_invoices)

        kpis.update(
            {
                "previous_total_revenue": previous_total_revenue,
                "previous_paid_invoice_count": previous_paid_invoice_count,
                "revenue_change_percent": _percent_change(total_revenue, previous_total_revenue),
                "paid_invoice_count_change_percent": _percent_change(paid_invoice_count, previous_paid_invoice_count),
            }
        )

    return {
        "scope": "self" if current_user.role == UserRole.STAFF else ("filtered" if seller_scope_id else "global"),
        "range_days": range_days,
        "as_of_date": report_day.isoformat(),
        "meta": {
            "trend_granularity": trend_granularity,
            "top_n": top_n,
            "staff_limit": staff_limit,
            "invoice_limit": invoice_limit,
            "include_context": include_context,
            "sold_by_id": seller_scope_id,
        },
        "kpis": kpis,
        "revenue_trend": revenue_trend,
        "payment_mix": payment_mix,
        "status_mix": status_mix,
        "top_products": top_products,
        "top_staff": top_staff,
        "top_invoices": [
            {
                "id": str(inv.id),
                "name": f"INV-{str(inv.id)[:8]}",
                "amount": float(inv.total_amount or 0),
                "status": _display_status(inv.status),
                "payment_method": _as_payment_method(inv.payment_method),
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "sold_by_id": str(inv.sold_by_id) if inv.sold_by_id else None,
            }
            for inv in top_invoices
        ],
    }


@router.get("/reports")
def get_dashboard_reports(
    range_days: int = Query(default=30, ge=1, le=365),
    as_of_date: date | None = Query(default=None),
    sold_by_id: str | None = Query(default=None),
    credit_limit: int = Query(default=8, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER)),
):
    report_day = as_of_date or date.today()
    today_start = datetime.combine(report_day, datetime.min.time())
    range_start = today_start - timedelta(days=range_days - 1)
    range_end = today_start + timedelta(days=1)

    invoice_query = _base_invoice_query(db, current_user, sold_by_id=sold_by_id)

    status_rows = (
        invoice_query
        .filter(Invoice.created_at >= range_start, Invoice.created_at < range_end)
        .with_entities(
            Invoice.status.label("status"),
            func.count(Invoice.id).label("count"),
            func.coalesce(func.sum(Invoice.total_amount), 0.0).label("amount"),
        )
        .group_by(Invoice.status)
        .all()
    )

    summary = {
        "DRAFT": {"count": 0, "amount": 0.0},
        "STAMPED": {"count": 0, "amount": 0.0},
        "DISPENSED": {"count": 0, "amount": 0.0},
        "CANCELLED": {"count": 0, "amount": 0.0},
    }
    for row in status_rows:
        key = _display_status(row.status)
        if key in summary:
            summary[key]["count"] = int(row.count or 0)
            summary[key]["amount"] = float(row.amount or 0)

    paid_revenue = float(summary["STAMPED"]["amount"] + summary["DISPENSED"]["amount"])
    cancelled_value = float(summary["CANCELLED"]["amount"])

    low_stock_items = (
        db.query(Product)
        .filter(
            Product.status == ProductStatus.ACTIVE,
            Product.reorder_level > 0,
            Product.quantity_on_hand <= Product.reorder_level,
        )
        .limit(10)
        .all()
    )
    out_of_stock_items = (
        db.query(Product)
        .filter(
            Product.status == ProductStatus.ACTIVE,
            Product.quantity_on_hand <= 0,
        )
        .order_by(Product.quantity_on_hand.asc(), Product.name.asc())
        .limit(50)
        .all()
    )

    paid_credit_invoices = (
        invoice_query
        .filter(
            Invoice.created_at >= range_start,
            Invoice.created_at < range_end,
            Invoice.status.in_(PAID_STATUSES),
        )
        .all()
    )
    credit_outstanding = sum(
        inv.total_amount or 0
        for inv in paid_credit_invoices
        if _as_payment_method(inv.payment_method) == "CREDIT"
    )

    recent_credit_candidates = (
        invoice_query
        .filter(Invoice.created_at >= range_start, Invoice.created_at < range_end)
        .order_by(desc(Invoice.created_at))
        .limit(300)
        .all()
    )
    credit_invoices = [
        inv for inv in recent_credit_candidates
        if _as_payment_method(inv.payment_method) == "CREDIT"
    ][:credit_limit]

    return {
        "scope": "filtered" if sold_by_id else "global",
        "range_days": range_days,
        "as_of_date": report_day.isoformat(),
        "kpis": {
            "paid_revenue": paid_revenue,
            "cancelled_value": cancelled_value,
            "credit_outstanding": float(credit_outstanding),
            "low_stock_items_count": len(low_stock_items),
        },
        "invoice_summary": {
            key: values["count"]
            for key, values in summary.items()
        },
        "low_stock_items": [
            {
                "id": str(p.id),
                "name": p.name,
                "quantity_on_hand": p.quantity_on_hand,
                "reorder_level": p.reorder_level,
            }
            for p in low_stock_items
        ],
        "out_of_stock_items": [
            {
                "id": str(p.id),
                "name": p.name,
                "quantity_on_hand": p.quantity_on_hand,
                "reorder_level": p.reorder_level,
            }
            for p in out_of_stock_items
        ],
        "credit_invoices": [
            {
                "id": str(inv.id),
                "name": f"INV-{str(inv.id)[:8]}",
                "status": _display_status(inv.status),
                "total_amount": float(inv.total_amount or 0),
                "payment_method": _as_payment_method(inv.payment_method),
                "sold_by_id": str(inv.sold_by_id) if inv.sold_by_id else None,
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
            }
            for inv in credit_invoices
        ],
    }


@router.get("/eod")
def get_end_of_day_report(
    range_days: int = Query(default=1, ge=1, le=365),
    as_of_date: date | None = Query(default=None),
    sold_by_id: str | None = Query(default=None),
    credit_limit: int = Query(default=8, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.CASHIER)),
):
    return get_dashboard_reports(
        range_days=range_days,
        as_of_date=as_of_date,
        sold_by_id=sold_by_id,
        credit_limit=credit_limit,
        db=db,
        current_user=current_user,
    )
