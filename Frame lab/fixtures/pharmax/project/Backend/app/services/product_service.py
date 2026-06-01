from sqlalchemy.orm import Session
from typing import List
from contextlib import contextmanager
from sqlalchemy import select
import re
from datetime import datetime, timezone
from example_projects.pharmax.Backend.app.models.product_table import Product, ProductType, ProductStatus
from example_projects.pharmax.Backend.app.models.stock_adjustment_table import StockAdjustment, StockAdjustmentStatus
from example_projects.pharmax.Backend.app.services.audit_service import AuditService
from example_projects.pharmax.Backend.app.models.product_unit_table import BaseUnit
from example_projects.pharmax.Backend.app.services.product_unit_service import ProductUnitService
from example_projects.pharmax.Backend.app.schemas.product_schema import CreateProduct


# SKU generation constants
TYPE_PREFIX = {ProductType.MEDICAL: "MED", ProductType.NON_MEDICAL: "NON"}
STOP_WORDS = {"TABLET", "TABLETS", "CAPSULE", "CAPSULES", "MG", "ML", "SYRUP", "CREAM", "OINTMENT"}


class ProductService:

    # ================= SKU =================

    @staticmethod
    def _generate_sku(db: Session, name: str, product_type: ProductType) -> str:
        type_prefix = TYPE_PREFIX.get(product_type, "GEN")

        tokens = re.findall(r"[A-Z0-9]+", name.upper())
        tokens = [t for t in tokens if t not in STOP_WORDS]

        name_code = "-".join(tokens[:3])[:10]
        base = f"{type_prefix}-{name_code}"

        seq = 1
        while True:
            sku = f"{base}-{seq:03d}"
            stmt = select(Product.id).where(Product.sku == sku)
            exists = db.execute(stmt).scalar_one_or_none()
            if not exists:
                return sku
            seq += 1

    @staticmethod
    def _validate_or_generate_sku(db: Session, name: str, product_type: ProductType) -> str:
        return ProductService._generate_sku(db, name, product_type)

    # ================= TX =================

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
    def create_product(db: Session, data: CreateProduct, user_id: str) -> Product:
    
        sku = ProductService._validate_or_generate_sku(db, data.name, data.product_type)

        with ProductService.transaction(db):
            product = Product(
                sku=sku,
                name=data.name,
                base_unit=data.base_unit,
                brand_name=data.brand_name,
                generic_name=data.generic_name,
                supplier_name=data.supplier_name,
                therapeutic_category=data.therapeutic_category,
                barcode=data.barcode,
                markup_percent=data.markup_percent,
                reorder_level=data.reorder_level,
                product_type=data.product_type,
                dispense_without_prescription=data.dispense_without_prescription,
                return_policy=data.return_policy,
                status=data.status,
                quantity_on_hand=data.initial_quantity,
            )

            db.add(product)
            db.flush()  # ensure product.id exists

            # Create the base unit
            ProductUnitService.create_unit(
                db,
                product_id=product.id,
                name=data.base_unit,
                price_per_unit=data.price_per_unit,
                multiplier_to_base=data.multiplier_to_base,
                user_id=user_id,
            )

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="CREATE",
                resource_type="PRODUCT",
                resource_id=product.id,
                details={
                    "sku": product.sku,
                    "name": product.name,
                    "product_type": product.product_type,
                },
            )

        db.refresh(product)  # now product.product_units contains the base unit automatically
        return product
    

    # ================= UPDATE =================

    @staticmethod
    def update_product(db: Session, product: Product, updates: dict, user_id: str | None = None) -> Product:
        old_values = {k: getattr(product, k) for k in updates}

        with ProductService.transaction(db):
            for field, value in updates.items():
                setattr(product, field, value)

            new_values = {k: getattr(product, k) for k in updates}

            if old_values != new_values:
                AuditService.log_action(
                    db=db,
                    user_id=user_id,
                    action="UPDATE",
                    resource_type="PRODUCT",
                    resource_id=product.id,
                    details={
                        "sku": product.sku,
                        "name": product.name,
                        "old_values": old_values,
                        "new_values": new_values,
                    },
                )

        db.refresh(product)
        return product

    # ================= DELETE =================

    @staticmethod
    def hard_delete_product(db: Session, product: Product, user_id: str | None = None) -> None:
        with ProductService.transaction(db):
            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="DELETE",
                resource_type="PRODUCT",
                resource_id=product.id,
                details={
                    "sku": product.sku,
                    "name": product.name,
                    "quantity_at_deletion": product.quantity_on_hand,
                },
            )
            

            db.delete(product)

    @staticmethod
    def soft_delete_product(db: Session, product: Product, user_id: str | None = None) -> None:
        with ProductService.transaction(db):
            product.status = ProductStatus.DELETED
            product.deleted_at = datetime.now(timezone.utc)

            AuditService.log_action(
                db=db,
                user_id=user_id,
                resource_id=product.id,
                resource_type="PRODUCT",
                action="SOFT_DELETE",
                details={
                    "sku": product.sku,
                    "name": product.name,
                    "quantity_at_deletion": product.quantity_on_hand,
                },
            )


    @staticmethod
    def restore_product(db: Session, product: Product, user_id: str | None):
        stmt = select(Product).where(Product.id == product.id, Product.deleted_at.isnot(None))
        product = db.execute(stmt).scalar_one_or_none()
        if not product:
            raise ValueError("Deleted product not found")

        with ProductService.transaction(db):
            product.status = ProductStatus.ACTIVE
            product.deleted_at = None

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="RESTORE_PRODUCT",
                resource_id=product.id,
                resource_type="PRODUCT",
                details={
                    "sku": product.sku,
                    "name": product.name,
                    "quantity_at_restore": product.quantity_on_hand,
                }
            )
    # ================= STOCK =================

    @staticmethod
    def adjust_stock(
        db: Session,
        product: Product,
        change_qty: int,
        reason: str,
        reference: str | None = None,
        note: str | None = None,
        user_id: str | None = None,
        requires_approval: bool = False,
        approval_note: str | None = None,
    ) -> StockAdjustment:

        old_qty = product.quantity_on_hand
        new_qty = old_qty + change_qty

        if not requires_approval and new_qty < 0:
            raise ValueError("Cannot adjust stock to a negative quantity")

        with ProductService.transaction(db):
            status = StockAdjustmentStatus.PENDING if requires_approval else StockAdjustmentStatus.APPROVED

            if not requires_approval:
                product.quantity_on_hand = new_qty

            adjustment = StockAdjustment(
                product_id=product.id,
                change_qty=change_qty,
                reason=reason,
                status=status,
                reference=reference,
                note=note,
                created_by_user_id=user_id,
                approved_by_user_id=user_id if not requires_approval else None,
                approved_at=datetime.now(timezone.utc) if not requires_approval else None,
                approval_note=(approval_note or "Auto-approved by admin") if not requires_approval else None,
            )

            db.add(adjustment)

            AuditService.log_action(
                db=db,
                user_id=user_id,
                action="REQUEST_STOCK_ADJUSTMENT" if requires_approval else "ADJUST_STOCK",
                resource_type="PRODUCT",
                resource_id=product.id,
                details={
                    "sku": product.sku,
                    "name": product.name,
                    "old_quantity": old_qty,
                    "new_quantity": old_qty if requires_approval else new_qty,
                    "change_qty": change_qty,
                    "reason": reason,
                    "reference": reference,
                    "status": status.value,
                    "approval_note": adjustment.approval_note,
                },
            )

        return adjustment

    @staticmethod
    def review_stock_adjustment(
        db: Session,
        product: Product,
        adjustment: StockAdjustment,
        approve: bool,
        reviewer_user_id: str,
        note: str | None = None,
    ) -> StockAdjustment:
        if adjustment.status != StockAdjustmentStatus.PENDING:
            raise ValueError("Only pending adjustments can be reviewed")

        old_qty = product.quantity_on_hand
        new_qty = old_qty + adjustment.change_qty

        if approve and new_qty < 0:
            raise ValueError("Cannot approve adjustment that would make stock negative")

        with ProductService.transaction(db):
            if approve:
                product.quantity_on_hand = new_qty
                adjustment.status = StockAdjustmentStatus.APPROVED
            else:
                adjustment.status = StockAdjustmentStatus.REJECTED

            adjustment.approved_by_user_id = reviewer_user_id
            adjustment.approved_at = datetime.now(timezone.utc)
            adjustment.approval_note = note

            AuditService.log_action(
                db=db,
                user_id=reviewer_user_id,
                action="APPROVE_STOCK_ADJUSTMENT" if approve else "REJECT_STOCK_ADJUSTMENT",
                resource_type="PRODUCT",
                resource_id=product.id,
                details={
                    "sku": product.sku,
                    "name": product.name,
                    "adjustment_id": adjustment.id,
                    "old_quantity": old_qty,
                    "new_quantity": product.quantity_on_hand,
                    "change_qty": adjustment.change_qty,
                    "reason": adjustment.reason.value if hasattr(adjustment.reason, "value") else adjustment.reason,
                    "review_status": adjustment.status.value,
                    "approval_note": note,
                },
            )

        return adjustment

    # ================= BULK IMPORT =================

    @staticmethod
    def _generate_sku_bulk(existing_skus: set, name: str, product_type: ProductType) -> str:
        """Generate a unique SKU without hitting the DB — uses an in-memory reserved set."""
        type_prefix = TYPE_PREFIX.get(product_type, "GEN")
        tokens = re.findall(r"[A-Z0-9]+", name.upper())
        tokens = [t for t in tokens if t not in STOP_WORDS]
        name_code = "-".join(tokens[:3])[:10]
        base = f"{type_prefix}-{name_code}"
        seq = 1
        while True:
            sku = f"{base}-{seq:03d}"
            if sku not in existing_skus:
                existing_skus.add(sku)
                return sku
            seq += 1

    @staticmethod
    def bulk_import(
        db: Session,
        rows: list[dict],
        user_id: str,
        skip_duplicates: bool = True,
    ) -> dict:
        """
        rows: list of dicts with keys matching CSV columns (already cleaned/mapped).
        Returns: {total, created, skipped, errors: [{row, name, reason}]}
        """
        from example_projects.pharmax.Backend.app.models.product_unit_table import ProductUnit

        # Pre-load existing SKUs and names to avoid per-row DB hits
        existing_skus: set = set(db.execute(select(Product.sku)).scalars().all())
        existing_names_lower: set = {
            n.lower() for n in db.execute(select(Product.name)).scalars().all()
        }

        created = 0
        skipped = 0
        errors: list[dict] = []

        for idx, row in enumerate(rows, start=2):  # row 1 = header
            name = (row.get("name") or "").strip()
            if not name:
                errors.append({"row": idx, "name": "—", "reason": "Empty product name"})
                continue

            if skip_duplicates and name.lower() in existing_names_lower:
                skipped += 1
                continue

            try:
                product_type_raw = (row.get("product_type") or "Non-medical").strip()
                product_type = (
                    ProductType.MEDICAL
                    if product_type_raw.lower() in ("medical", "med")
                    else ProductType.NON_MEDICAL
                )

                sku = ProductService._generate_sku_bulk(existing_skus, name, product_type)

                # Parse optional numeric fields safely
                def _int(v, default=0):
                    try:
                        return int(float(str(v).replace(",", "").strip()))
                    except (TypeError, ValueError):
                        return default

                def _float(v, default=None):
                    try:
                        return float(str(v).replace(",", "").strip())
                    except (TypeError, ValueError):
                        return default

                def _bool(v, default=True):
                    if isinstance(v, bool):
                        return v
                    s = str(v).strip().lower()
                    if s in ("yes", "true", "1", "y"):
                        return True
                    if s in ("no", "false", "0", "n"):
                        return False
                    return default

                status_raw = (row.get("status") or "Active").strip().capitalize()
                status_map = {"Active": ProductStatus.ACTIVE, "Inactive": ProductStatus.INACTIVE}
                status = status_map.get(status_raw, ProductStatus.ACTIVE)

                product = Product(
                    sku=sku,
                    name=name,
                    base_unit=BaseUnit.PACK,
                    brand_name=row.get("brand_name") or None,
                    generic_name=row.get("generic_name") or None,
                    supplier_name=row.get("supplier_name") or None,
                    barcode=row.get("barcode") or None,
                    markup_percent=_float(row.get("markup_percent")),
                    reorder_level=_int(row.get("reorder_level"), 0),
                    product_type=product_type,
                    dispense_without_prescription=_bool(row.get("dispense_without_prescription"), True),
                    return_policy=row.get("return_policy") or None,
                    status=status,
                    quantity_on_hand=_int(row.get("initial_quantity"), 0),
                )
                db.add(product)
                db.flush()

                unit = ProductUnit(
                    product_id=product.id,
                    name=BaseUnit.PACK,
                    price_per_unit=_float(row.get("price_per_unit"), 0.0),
                    multiplier_to_base=1,
                )
                db.add(unit)

                existing_names_lower.add(name.lower())
                created += 1

                # Commit in batches of 200 to keep memory usage low
                if created % 200 == 0:
                    db.commit()

            except Exception as exc:
                db.rollback()
                errors.append({"row": idx, "name": name, "reason": str(exc)})
                # Re-seed the sets after rollback
                existing_skus = set(db.execute(select(Product.sku)).scalars().all())
                existing_names_lower = {
                    n.lower() for n in db.execute(select(Product.name)).scalars().all()
                }

        db.commit()

        return {
            "total": len(rows),
            "created": created,
            "skipped": skipped,
            "errors": errors,
        }

    # ================= READ =================

    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Product | None:
        stmt = select(Product).where(Product.id == product_id, Product.deleted_at.is_(None))
        return db.execute(stmt).scalar_one_or_none()
    

    @staticmethod
    def list_products(
        db: Session,
        name_filter: str | None = None,
        generic_name_filter: str | None = None,
        therapeutic_category_filter: str | None = None,
        min_stock: int | None = None,
        limit: int = 50,
        offset: int = 0,
        deleted: bool = False,
    ) -> List[Product]:

        if deleted:
            stmt = select(Product).where(Product.deleted_at.isnot(None))
        else:
            stmt = select(Product).where(Product.deleted_at.is_(None))

        if name_filter:
            stmt = stmt.where(Product.name.ilike(f"%{name_filter}%"))
        if generic_name_filter:
            stmt = stmt.where(Product.generic_name.ilike(f"%{generic_name_filter}%"))
        if therapeutic_category_filter:
            stmt = stmt.where(Product.therapeutic_category == therapeutic_category_filter)
        if min_stock is not None:
            stmt = stmt.where(Product.quantity_on_hand >= min_stock)

        stmt = stmt.order_by(Product.name).offset(offset).limit(limit)
        return db.execute(stmt).scalars().all()
    
