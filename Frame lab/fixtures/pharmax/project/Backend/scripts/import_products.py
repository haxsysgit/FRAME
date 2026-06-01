#!/usr/bin/env python3
"""
Product Data Import Script
Imports products from CSV file into the database
"""
import csv
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from example_projects.pharmax.Backend.app.db.session import SessionLocal
from example_projects.pharmax.Backend.app.models import Product
from example_projects.pharmax.Backend.app.core.security import get_password_hash


def import_products_from_csv(csv_path: str, db: Session):
    """Import products from CSV file"""
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products_created = 0
        products_updated = 0
        
        for row in reader:
            product_name = row.get('PRODUCT NAME', '').strip()
            if not product_name:
                continue
            
            # Parse fields
            brand_name = row.get('BRAND NAME', '').strip() or None
            supplier_name = row.get('SUPPLIER', '').strip() or None
            barcode = row.get('BARCODE', '').strip() or None
            markup_str = row.get('MARKUP', '').strip()
            stock_str = row.get('STOCK', '').strip()
            threshold_str = row.get('STOCK THRESHOLD', '').strip()
            status_str = row.get('STATUS', 'Active').strip()
            product_type_str = row.get('TYPE', 'Non-medical').strip()
            dispense_str = row.get('DISPENSE WITHOUT PRESCRIPTION', 'Yes').strip()
            return_policy = row.get('ITEM RETURN POLICY', '').strip() or None
            
            # Parse numeric values
            try:
                markup = float(markup_str) if markup_str else 0.0
            except ValueError:
                markup = 0.0
            
            try:
                stock = int(stock_str) if stock_str else 0
            except ValueError:
                stock = 0
            
            try:
                threshold = int(threshold_str) if threshold_str else 5
            except ValueError:
                threshold = 5
            
            # Map product type
            from example_projects.pharmax.Backend.app.models.product_table import ProductType, ProductStatus
            product_type = ProductType.MEDICAL if product_type_str == 'Medical' else ProductType.NON_MEDICAL
            status = ProductStatus.ACTIVE if status_str.lower() == 'active' else ProductStatus.INACTIVE
            dispense_without_rx = dispense_str.lower() == 'yes'
            
            # Generate SKU (simple counter-based for now)
            import hashlib
            sku = hashlib.md5(f"{product_name}_{brand_name}".encode()).hexdigest()[:12].upper()
            
            # Check if product exists (by name and brand combination)
            existing = db.query(Product).filter(
                Product.name == product_name,
                Product.brand_name == brand_name
            ).first()
            
            if existing:
                # Update existing product
                existing.supplier_name = supplier_name
                existing.barcode = barcode
                existing.markup_percent = markup
                existing.quantity_on_hand = stock
                existing.reorder_level = threshold
                existing.status = status
                existing.return_policy = return_policy
                products_updated += 1
            else:
                # Create new product
                from example_projects.pharmax.Backend.app.models.product_table import BaseUnit
                product = Product(
                    sku=sku,
                    name=product_name,
                    brand_name=brand_name,
                    supplier_name=supplier_name,
                    barcode=barcode,
                    markup_percent=markup,
                    quantity_on_hand=stock,
                    reorder_level=threshold,
                    product_type=product_type,
                    dispense_without_prescription=dispense_without_rx,
                    return_policy=return_policy,
                    status=status,
                    base_unit=BaseUnit.PACK
                )
                db.add(product)
                products_created += 1
        
        db.commit()
        print(f"✅ Import complete!")
        print(f"   - Created: {products_created} products")
        print(f"   - Updated: {products_updated} products")
        print(f"   - Total: {products_created + products_updated} products")


def main():
    """Main import function"""
    csv_path = Path(__file__).parent.parent.parent / 'data' / 'Product Master List.csv'
    
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"📦 Importing products from {csv_path}")
    
    db = SessionLocal()
    try:
        import_products_from_csv(str(csv_path), db)
    except Exception as e:
        print(f"❌ Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
