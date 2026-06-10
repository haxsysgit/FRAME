"""
Seed real product data from the pharmacy CSV into the database.

Usage:
    uv run python scripts/seed_products.py
    uv run python scripts/seed_products.py --csv /path/to/other.csv
    uv run python scripts/seed_products.py --clear   # wipe products first
"""
import argparse
import csv
import random
import sys
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import select, text
from example_projects.pharmax.Backend.app.db.session import SessionLocal
from example_projects.pharmax.Backend.app.models.product_table import Product, ProductType, ProductStatus
from example_projects.pharmax.Backend.app.models.product_unit_table import ProductUnit, BaseUnit
from example_projects.pharmax.Backend.app.services.product_service import ProductService
from example_projects.pharmax.Backend.app.schemas.product_schema import CreateProduct

DEFAULT_CSV = (
    Path(__file__).resolve().parents[2] / "data" / "Product Master List copy.csv"
)

# ── helpers ─────────────────────────────────────────────────────────────────

def _safe_float(val: str, default: float = 0.0) -> float:
    try:
        return float(val.strip()) if val.strip() else default
    except ValueError:
        return default


def _safe_int(val: str, default: int = 0) -> int:
    try:
        return int(float(val.strip())) if val.strip() else default
    except ValueError:
        return default


def _map_status(raw: str) -> ProductStatus:
    s = raw.strip().lower()
    if s == "active":
        return ProductStatus.ACTIVE
    # "Pending" and anything else → Inactive (no Pending in backend enum)
    return ProductStatus.INACTIVE


def _map_type(raw: str) -> ProductType:
    return ProductType.MEDICAL if raw.strip().lower() == "medical" else ProductType.NON_MEDICAL


def _map_dispense(raw: str) -> bool:
    return raw.strip().lower() == "yes"


def _random_initial_price() -> float:
    return round(random.uniform(100.0, 5000.0), 2)


# ── main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed pharmacy products from CSV.")
    parser.add_argument("--csv", default=str(DEFAULT_CSV), help="Path to product CSV file")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete ALL existing products before seeding (use with caution)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only import the first N rows (useful for testing)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        raise SystemExit(f"CSV file not found: {csv_path}")

    db = SessionLocal()
    try:
        if args.clear:
            print("⚠  Clearing existing products and units…")
            db.execute(text("DELETE FROM product_units"))
            db.execute(text("DELETE FROM products"))
            db.commit()
            print("   Done.\n")

        with open(csv_path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if args.limit:
            rows = rows[: args.limit]

        total = len(rows)
        print(f"Importing {total} products from: {csv_path.name}\n")

        created = 0
        skipped = 0
        errors = 0

        for i, row in enumerate(rows, 1):
            name = row.get("PRODUCT NAME", "").strip()
            if not name:
                skipped += 1
                continue

            # Check duplicate by name (case-insensitive exact match)
            existing = db.execute(
                select(Product.id).where(Product.name == name).limit(1)
            ).scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            try:
                data = CreateProduct(
                    name=name,
                    brand_name=row.get("BRAND NAME", "").strip() or None,
                    supplier_name=row.get("SUPPLIER", "").strip() or None,
                    barcode=row.get("BARCODE", "").strip() or None,
                    markup_percent=_safe_float(row.get("MARKUP", ""), 0.0) or None,
                    reorder_level=_safe_int(row.get("STOCK THRESHOLD", ""), 5),
                    initial_quantity=_safe_int(row.get("STOCK", ""), 0),
                    product_type=_map_type(row.get("TYPE", "Non-medical")),
                    dispense_without_prescription=_map_dispense(
                        row.get("DISPENSE WITHOUT PRESCRIPTION", "Yes")
                    ),
                    return_policy=row.get("ITEM RETURN POLICY", "").strip() or None,
                    status=_map_status(row.get("STATUS", "Active")),
                    # Required unit fields — default Pack / randomized starter price for testing.
                    base_unit=BaseUnit.PACK,
                    price_per_unit=_random_initial_price(),
                    multiplier_to_base=1.0,
                )
                ProductService.create_product(db=db, data=data, user_id="system")
                created += 1

                if i % 100 == 0 or i == total:
                    pct = int(i / total * 100)
                    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                    print(f"\r  [{bar}] {pct:3d}%  {i}/{total}", end="", flush=True)

            except Exception as exc:
                errors += 1
                if errors <= 5:
                    print(f"\n  ⚠ Row {i} ({name[:40]}): {exc}")

        print(f"\n\n✅  Done.")
        print(f"   Created : {created}")
        print(f"   Skipped : {skipped}  (duplicates / blank names)")
        print(f"   Errors  : {errors}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
