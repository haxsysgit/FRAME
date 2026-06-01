from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum
from sqlalchemy import Numeric, Float, Integer, String, Uuid, func
from sqlalchemy.orm import relationship

from example_projects.pharmax.Backend.app.db.base import Base
from example_projects.pharmax.Backend.app.models.product_unit_table import BaseUnit


# High-level classification for your CSV TYPE column.
class ProductType(str, Enum):
    MEDICAL = "Medical"
    NON_MEDICAL = "Non-medical"


# Therapeutic categories for symptom-based drug lookup (Scenario 2).
class TherapeuticCategory(str, Enum):
    ANALGESIC = "Analgesic"
    ANTI_MALARIAL = "Anti-malarial"
    ANTIBIOTIC = "Antibiotic"
    ANTI_FUNGAL = "Anti-fungal"
    ANTI_INFLAMMATORY = "Anti-inflammatory"
    ANTI_DIARRHOEAL = "Anti-diarrhoeal"
    ANTACID = "Antacid"
    ANTIHISTAMINE = "Antihistamine"
    ANTIHYPERTENSIVE = "Antihypertensive"
    ANTI_DIABETIC = "Anti-diabetic"
    COUGH_AND_COLD = "Cough & Cold"
    VITAMIN_SUPPLEMENT = "Vitamin & Supplement"
    SKIN_CARE = "Skin Care"
    EYE_EAR_NOSE = "Eye/Ear/Nose"
    GASTROINTESTINAL = "Gastrointestinal"
    CONTRACEPTIVE = "Contraceptive"
    OTHER = "Other"


class ProductStatus(str, Enum):
    ACTIVE = "Active"
    DELETED = "Deleted"
    INACTIVE = "Inactive"


# Main inventory item table.
class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))

    # Human-friendly code you generate (unique).
    sku = Column(String(255), nullable=False, unique=True, index=True)

    # Product name; indexed for fast search in the invoice flow.
    name = Column(String(255), nullable=False, index=True)
    base_unit = Column(SAEnum(BaseUnit, name="baseunit"), nullable=False, default=BaseUnit.PACK)
    # Optional metadata for better product identification and categorization.
    brand_name = Column(String(255), nullable=True)
    generic_name = Column(String(255), nullable=True, index=True)
    supplier_name = Column(String(255), nullable=True)
    therapeutic_category = Column(
        SAEnum(TherapeuticCategory, name="therapeuticcategory"),
        nullable=True,
        index=True,
    )
    barcode = Column(String(255), nullable=True, index=True)
    markup_percent = Column(Numeric(10, 2), nullable=True)

    # Current stock snapshot (fast to read).
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=0)
    product_type = Column(SAEnum(ProductType, name="producttype"), nullable=False)
    dispense_without_prescription = Column(Boolean, nullable=False, default=True)
    return_policy = Column(String(255), nullable=True)
    status = Column(SAEnum(ProductStatus, name="productstatus"), nullable=False, default=ProductStatus.ACTIVE)

    # Timestamps (created_at set by DB; updated_at auto-updates on change).
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, default=None)


    # One-to-many relationship: one Product has many StockAdjustment rows.
    # `back_populates` must match the attribute name on the other model.
    # `cascade` controls what happens to adjustments when you operate on Product.
    adjustments = relationship(
        "StockAdjustment", back_populates="product", cascade="all, delete-orphan"
    )

    product_units = relationship(
        "ProductUnit", back_populates="product", cascade="all, delete-orphan"
    )
    
    # Relationship to invoice items (for checking delete constraints)
    invoice_items = relationship("InvoiceItem", back_populates="product")
