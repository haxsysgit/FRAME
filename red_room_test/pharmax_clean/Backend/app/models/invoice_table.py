from uuid import uuid4
from sqlalchemy import Column, String, DateTime, Numeric, func, Enum as SAEnum, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from example_projects.pharmax.Backend.app.db.base import Base
from enum import Enum

class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"
    DISPENSED = "DISPENSED"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    sold_by_id = Column(Uuid(as_uuid=False), ForeignKey("users.id"), nullable=False)
    finalized_by_id = Column(Uuid(as_uuid=False), ForeignKey("users.id"), nullable=True)
    dispensed_by_id = Column(Uuid(as_uuid=False), ForeignKey("users.id"), nullable=True)
    
    status = Column(SAEnum(InvoiceStatus), nullable=False, default=InvoiceStatus.DRAFT)
    payment_method = Column(SAEnum(PaymentMethod), nullable=True)
    total_amount = Column(Numeric(10, 5), nullable=True)
    cashier_note = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    finalized_at = Column(DateTime, nullable=True)
    dispensed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", foreign_keys=[sold_by_id], back_populates="invoices")
    finalized_by = relationship("User", foreign_keys=[finalized_by_id])
    dispensed_by = relationship("User", foreign_keys=[dispensed_by_id])
    
    items = relationship(
        "InvoiceItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="joined",
    )
