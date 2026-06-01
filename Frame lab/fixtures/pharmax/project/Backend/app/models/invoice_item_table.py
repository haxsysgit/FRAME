from uuid import uuid4
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Uuid
from sqlalchemy.orm import relationship
from example_projects.pharmax.Backend.app.db.base import Base



class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    invoice_id = Column(Uuid(as_uuid=False), ForeignKey("invoices.id"), nullable=False, index=True)
    product_id = Column(Uuid(as_uuid=False), ForeignKey("products.id"), nullable=False, index=True)
    product_unit_id = Column(Uuid(as_uuid=False), ForeignKey("product_units.id"), nullable=False, index=True)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 5), nullable=False)
    line_total = Column(Numeric(10, 5), nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
    product_unit = relationship("ProductUnit")
    
    
