#!/usr/bin/env python3
"""
Seed the database with 1500 realistic pharmaceutical products with proper pricing.
This creates a comprehensive inventory suitable for development and testing.
"""
import sys
import random
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from example_projects.pharmax.Backend.app.db.session import SessionLocal
from example_projects.pharmax.Backend.app.models.product_table import Product, ProductType, ProductStatus, TherapeuticCategory
from example_projects.pharmax.Backend.app.models.product_unit_table import ProductUnit, BaseUnit
from example_projects.pharmax.Backend.app.services.product_service import ProductService


# Realistic product templates
PRODUCT_TEMPLATES = [
    # Pain & Fever
    {"name": "Paracetamol", "category": TherapeuticCategory.ANALGESIC, "base_unit": BaseUnit.TABLET, "base_price": 50, "variations": ["500mg", "1000mg", "Syrup"]},
    {"name": "Ibuprofen", "category": TherapeuticCategory.ANTI_INFLAMMATORY, "base_unit": BaseUnit.TABLET, "base_price": 100, "variations": ["200mg", "400mg", "600mg"]},
    {"name": "Aspirin", "category": TherapeuticCategory.ANALGESIC, "base_unit": BaseUnit.TABLET, "base_price": 80, "variations": ["75mg", "100mg", "300mg"]},
    {"name": "Diclofenac", "category": TherapeuticCategory.ANTI_INFLAMMATORY, "base_unit": BaseUnit.TABLET, "base_price": 150, "variations": ["50mg", "75mg", "Gel"]},
    {"name": "Tramadol", "category": TherapeuticCategory.ANALGESIC, "base_unit": BaseUnit.CAPSULE, "base_price": 200, "variations": ["50mg", "100mg"]},
    
    # Antibiotics
    {"name": "Amoxicillin", "category": TherapeuticCategory.ANTIBIOTIC, "base_unit": BaseUnit.CAPSULE, "base_price": 150, "variations": ["250mg", "500mg", "Syrup"]},
    {"name": "Azithromycin", "category": TherapeuticCategory.ANTIBIOTIC, "base_unit": BaseUnit.TABLET, "base_price": 300, "variations": ["250mg", "500mg"]},
    {"name": "Ciprofloxacin", "category": TherapeuticCategory.ANTIBIOTIC, "base_unit": BaseUnit.TABLET, "base_price": 200, "variations": ["250mg", "500mg", "750mg"]},
    {"name": "Metronidazole", "category": TherapeuticCategory.ANTIBIOTIC, "base_unit": BaseUnit.TABLET, "base_price": 120, "variations": ["200mg", "400mg", "500mg"]},
    {"name": "Ceftriaxone", "category": TherapeuticCategory.ANTIBIOTIC, "base_unit": BaseUnit.VIAL, "base_price": 500, "variations": ["1g", "2g"]},
    
    # Anti-malarials
    {"name": "Artemether/Lumefantrine", "category": TherapeuticCategory.ANTI_MALARIAL, "base_unit": BaseUnit.TABLET, "base_price": 800, "variations": ["Adult", "Child"]},
    {"name": "Artesunate", "category": TherapeuticCategory.ANTI_MALARIAL, "base_unit": BaseUnit.TABLET, "base_price": 600, "variations": ["50mg", "100mg", "Injection"]},
    {"name": "Chloroquine", "category": TherapeuticCategory.ANTI_MALARIAL, "base_unit": BaseUnit.TABLET, "base_price": 100, "variations": ["250mg", "Syrup"]},
    {"name": "Quinine", "category": TherapeuticCategory.ANTI_MALARIAL, "base_unit": BaseUnit.TABLET, "base_price": 150, "variations": ["300mg", "Injection"]},
    
    # Cold & Cough
    {"name": "Benylin", "category": TherapeuticCategory.COUGH_AND_COLD, "base_unit": BaseUnit.SYRUP, "base_price": 1200, "variations": ["Adult", "Paediatric", "Expectorant"]},
    {"name": "Coflin", "category": TherapeuticCategory.COUGH_AND_COLD, "base_unit": BaseUnit.SYRUP, "base_price": 800, "variations": ["Regular", "Plus"]},
    {"name": "Actifed", "category": TherapeuticCategory.COUGH_AND_COLD, "base_unit": BaseUnit.TABLET, "base_price": 400, "variations": ["Regular", "Plus"]},
    {"name": "Loratadine", "category": TherapeuticCategory.ANTIHISTAMINE, "base_unit": BaseUnit.TABLET, "base_price": 250, "variations": ["10mg"]},
    {"name": "Cetirizine", "category": TherapeuticCategory.ANTIHISTAMINE, "base_unit": BaseUnit.TABLET, "base_price": 200, "variations": ["10mg"]},
    
    # Antacids & GI
    {"name": "Omeprazole", "category": TherapeuticCategory.ANTACID, "base_unit": BaseUnit.CAPSULE, "base_price": 300, "variations": ["20mg", "40mg"]},
    {"name": "Ranitidine", "category": TherapeuticCategory.ANTACID, "base_unit": BaseUnit.TABLET, "base_price": 150, "variations": ["150mg", "300mg"]},
    {"name": "Gaviscon", "category": TherapeuticCategory.ANTACID, "base_unit": BaseUnit.SUSPENSION, "base_price": 1500, "variations": ["Regular", "Extra Strength"]},
    {"name": "Loperamide", "category": TherapeuticCategory.ANTI_DIARRHOEAL, "base_unit": BaseUnit.CAPSULE, "base_price": 200, "variations": ["2mg"]},
    
    # Vitamins & Supplements
    {"name": "Vitamin C", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.TABLET, "base_price": 500, "variations": ["500mg", "1000mg", "Chewable"]},
    {"name": "Multivitamin", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.TABLET, "base_price": 800, "variations": ["Adult", "Children", "Senior"]},
    {"name": "Vitamin D3", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.CAPSULE, "base_price": 1200, "variations": ["1000IU", "5000IU"]},
    {"name": "Calcium", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.TABLET, "base_price": 600, "variations": ["500mg", "Plus D3"]},
    {"name": "Iron Supplement", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.TABLET, "base_price": 700, "variations": ["Ferrous Sulphate", "Ferrous Fumarate"]},
    
    # Diabetes
    {"name": "Metformin", "category": TherapeuticCategory.ANTI_DIABETIC, "base_unit": BaseUnit.TABLET, "base_price": 200, "variations": ["500mg", "850mg", "1000mg"]},
    {"name": "Glibenclamide", "category": TherapeuticCategory.ANTI_DIABETIC, "base_unit": BaseUnit.TABLET, "base_price": 150, "variations": ["5mg"]},
    {"name": "Insulin", "category": TherapeuticCategory.ANTI_DIABETIC, "base_unit": BaseUnit.VIAL, "base_price": 3500, "variations": ["Regular", "NPH", "Mix"]},
    
    # Hypertension
    {"name": "Amlodipine", "category": TherapeuticCategory.ANTIHYPERTENSIVE, "base_unit": BaseUnit.TABLET, "base_price": 200, "variations": ["5mg", "10mg"]},
    {"name": "Lisinopril", "category": TherapeuticCategory.ANTIHYPERTENSIVE, "base_unit": BaseUnit.TABLET, "base_price": 250, "variations": ["10mg", "20mg"]},
    {"name": "Losartan", "category": TherapeuticCategory.ANTIHYPERTENSIVE, "base_unit": BaseUnit.TABLET, "base_price": 300, "variations": ["50mg", "100mg"]},
    {"name": "Atenolol", "category": TherapeuticCategory.ANTIHYPERTENSIVE, "base_unit": BaseUnit.TABLET, "base_price": 180, "variations": ["50mg", "100mg"]},
    
    # Skin Care
    {"name": "Hydrocortisone Cream", "category": TherapeuticCategory.SKIN_CARE, "base_unit": BaseUnit.CREAM, "base_price": 800, "variations": ["1%", "2.5%"]},
    {"name": "Betamethasone", "category": TherapeuticCategory.SKIN_CARE, "base_unit": BaseUnit.CREAM, "base_price": 1200, "variations": ["Cream", "Ointment"]},
    {"name": "Clotrimazole", "category": TherapeuticCategory.ANTI_FUNGAL, "base_unit": BaseUnit.CREAM, "base_price": 600, "variations": ["1%", "Pessary"]},
    {"name": "Miconazole", "category": TherapeuticCategory.ANTI_FUNGAL, "base_unit": BaseUnit.CREAM, "base_price": 700, "variations": ["2%"]},
    
    # Eye/Ear/Nose
    {"name": "Eye Drops", "category": TherapeuticCategory.EYE_EAR_NOSE, "base_unit": BaseUnit.DROPS, "base_price": 500, "variations": ["Antibiotic", "Lubricant", "Antihistamine"]},
    {"name": "Ear Drops", "category": TherapeuticCategory.EYE_EAR_NOSE, "base_unit": BaseUnit.DROPS, "base_price": 450, "variations": ["Wax Softener", "Antibiotic"]},
    {"name": "Nasal Spray", "category": TherapeuticCategory.EYE_EAR_NOSE, "base_unit": BaseUnit.BOTTLE, "base_price": 800, "variations": ["Decongestant", "Saline"]},
    
    # Gastrointestinal
    {"name": "Bisacodyl", "category": TherapeuticCategory.GASTROINTESTINAL, "base_unit": BaseUnit.TABLET, "base_price": 150, "variations": ["5mg", "10mg"]},
    {"name": "Lactulose", "category": TherapeuticCategory.GASTROINTESTINAL, "base_unit": BaseUnit.SYRUP, "base_price": 1200, "variations": ["Regular"]},
    {"name": "Mebendazole", "category": TherapeuticCategory.GASTROINTESTINAL, "base_unit": BaseUnit.TABLET, "base_price": 200, "variations": ["100mg", "500mg"]},
    
    # Contraceptives
    {"name": "Combined Oral Contraceptive", "category": TherapeuticCategory.CONTRACEPTIVE, "base_unit": BaseUnit.PACK, "base_price": 1500, "variations": ["Low Dose", "Standard"]},
    {"name": "Emergency Contraceptive", "category": TherapeuticCategory.CONTRACEPTIVE, "base_unit": BaseUnit.TABLET, "base_price": 2000, "variations": ["Single Dose", "Two Dose"]},
    
    # Additional Common Medicines
    {"name": "Prednisolone", "category": TherapeuticCategory.ANTI_INFLAMMATORY, "base_unit": BaseUnit.TABLET, "base_price": 180, "variations": ["5mg", "10mg", "25mg"]},
    {"name": "Dexamethasone", "category": TherapeuticCategory.ANTI_INFLAMMATORY, "base_unit": BaseUnit.TABLET, "base_price": 200, "variations": ["0.5mg", "4mg"]},
    {"name": "Salbutamol", "category": TherapeuticCategory.OTHER, "base_unit": BaseUnit.BOTTLE, "base_price": 1500, "variations": ["Inhaler", "Syrup"]},
    {"name": "Folic Acid", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.TABLET, "base_price": 300, "variations": ["5mg", "Plus Iron"]},
    {"name": "Zinc Supplement", "category": TherapeuticCategory.VITAMIN_SUPPLEMENT, "base_unit": BaseUnit.TABLET, "base_price": 500, "variations": ["Regular", "Plus Vitamin C"]},
]

BRANDS = ["Emzor", "Fidson", "GSK", "Pfizer", "May & Baker", "Evans", "Pharma Deko", "Neimeth", "Swiss Pharma", "Drugfield"]
GENERIC_SUFFIX = ["Forte", "Plus", "SR", "XR", "Duo", "Complex", "Max", "Pro", "Extra", "Premium", "Ultra", "Advanced"]


def create_product_with_units(db: Session, template: dict, brand: str, variation: str, variation_idx: int) -> Product:
    """Create a product with its pricing units."""
    
    # Generate product details
    product_name = f"{template['name']} {variation}"
    if random.random() > 0.6:
        product_name += f" [{brand}]"
    
    # Determine product type
    is_medical = template['category'] not in [
        TherapeuticCategory.VITAMIN_SUPPLEMENT,
        TherapeuticCategory.SKIN_CARE
    ]
    product_type = ProductType.MEDICAL if is_medical else ProductType.NON_MEDICAL
    
    # Use ProductService to generate SKU
    sku = ProductService._validate_or_generate_sku(db, product_name, product_type)
    
    # Calculate price variation
    base_price = template['base_price']
    price_multiplier = 1 + (variation_idx * 0.3) + random.uniform(-0.2, 0.4)
    unit_price = round(base_price * price_multiplier, 2)
    
    # Stock levels
    stock = random.randint(0, 500)
    reorder_level = random.randint(10, 50)
    
    # Create product
    product = Product(
        sku=sku,
        name=product_name,
        brand_name=brand if random.random() > 0.3 else None,
        generic_name=template['name'],
        supplier_name=random.choice(BRANDS) if random.random() > 0.5 else None,
        therapeutic_category=template['category'],
        barcode=f"6{random.randint(100000000000, 999999999999)}",
        markup_percent=random.uniform(20, 80),
        quantity_on_hand=stock,
        reorder_level=reorder_level,
        product_type=product_type,
        dispense_without_prescription=(product_type == ProductType.NON_MEDICAL or random.random() > 0.7),
        return_policy="non-approval" if random.random() > 0.5 else "approval",
        status=ProductStatus.ACTIVE if stock > 0 or random.random() > 0.2 else ProductStatus.INACTIVE,
        base_unit=template['base_unit']
    )
    
    db.add(product)
    db.flush()  # Get the product ID
    
    # Create base unit pricing
    base_unit = ProductUnit(
        product_id=product.id,
        name=template['base_unit'],
        multiplier_to_base=1,
        price_per_unit=unit_price,
        is_default=True
    )
    db.add(base_unit)
    
    # Add additional units (pack, box, carton for bulk pricing)
    if random.random() > 0.5:
        # Pack of 10
        pack_unit = ProductUnit(
            product_id=product.id,
            name=BaseUnit.PACK,
            multiplier_to_base=10,
            price_per_unit=round(unit_price * 10 * 0.9, 2),  # 10% discount
            is_default=False
        )
        db.add(pack_unit)
    
    if random.random() > 0.7:
        # Box of 100
        box_unit = ProductUnit(
            product_id=product.id,
            name=BaseUnit.BOX,
            multiplier_to_base=100,
            price_per_unit=round(unit_price * 100 * 0.85, 2),  # 15% discount
            is_default=False
        )
        db.add(box_unit)
    
    return product


def seed_realistic_products(db: Session):
    """Seed database with 3000+ realistic products."""
    
    print("🗑️  Clearing existing products...")
    db.query(ProductUnit).delete()
    db.query(Product).delete()
    db.commit()
    
    print("📦 Generating 3000+ realistic pharmaceutical products...")
    
    products_created = 0
    target_count = 3000
    
    while products_created < target_count:
        for template in PRODUCT_TEMPLATES:
            if products_created >= target_count:
                break
            
            # Create products for each variation
            for variation_idx, variation in enumerate(template['variations']):
                if products_created >= target_count:
                    break
                
                # Use different brands
                brand = random.choice(BRANDS)
                
                try:
                    product = create_product_with_units(db, template, brand, variation, variation_idx)
                    products_created += 1
                    
                    if products_created % 100 == 0:
                        print(f"   Created {products_created} products...")
                        db.commit()  # Commit in batches
                
                except Exception as e:
                    print(f"   ⚠️  Error creating product: {e}")
                    continue
        
        # If we haven't reached target, create generic variations
        if products_created < target_count:
            for template in PRODUCT_TEMPLATES:
                if products_created >= target_count:
                    break
                
                for suffix in GENERIC_SUFFIX:
                    if products_created >= target_count:
                        break
                    
                    brand = random.choice(BRANDS)
                    variation = f"{random.choice(template['variations'])} {suffix}"
                    
                    try:
                        product = create_product_with_units(db, template, brand, variation, 0)
                        products_created += 1
                        
                        if products_created % 100 == 0:
                            print(f"   Created {products_created} products...")
                            db.commit()
                    except Exception as e:
                        continue
    
    db.commit()
    
    # Print summary
    print("\n✅ Product seeding complete!")
    print(f"   Total products created: {products_created}")
    
    # Stats
    total_units = db.query(ProductUnit).count()
    active_products = db.query(Product).filter(Product.status == ProductStatus.ACTIVE).count()
    in_stock = db.query(Product).filter(Product.quantity_on_hand > 0).count()
    
    print(f"   Total pricing units: {total_units}")
    print(f"   Active products: {active_products}")
    print(f"   Products in stock: {in_stock}")
    
    # Sample prices
    print("\n💰 Sample pricing:")
    samples = db.query(Product, ProductUnit).join(ProductUnit).filter(
        ProductUnit.is_default == True
    ).limit(5).all()
    
    for product, unit in samples:
        print(f"   {product.name[:40]:40} - ₦{unit.price_per_unit:,.2f}")


def main():
    print("=" * 70)
    print("PHARMAX - Realistic Product Data Seeder")
    print("=" * 70)
    print()
    
    db = SessionLocal()
    try:
        seed_realistic_products(db)
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
    
    print("\n" + "=" * 70)
    print("Seeding complete. You can now test the application with realistic data.")
    print("=" * 70)


if __name__ == "__main__":
    main()
