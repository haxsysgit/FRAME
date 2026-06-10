from sqlalchemy import String, Boolean, DateTime, Uuid
from example_projects.pharmax.Backend.app.db.base import Base
from sqlalchemy import func,Enum as SAEnum
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import relationship

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CASHIER = "CASHIER"
    STAFF = "STAFF"



class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_pin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
    )
    audit_logs = relationship("AuditLog", back_populates="user")
    invoices = relationship("Invoice", back_populates="user", foreign_keys="[Invoice.sold_by_id]")
    adjustments = relationship("StockAdjustment", back_populates="user", foreign_keys="[StockAdjustment.created_by_user_id]")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_logout_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    @property
    def is_online(self) -> bool:
        if not self.last_seen_at:
            return False

        if self.last_logout_at and self.last_seen_at <= self.last_logout_at:
            return False

        return self.last_seen_at >= (datetime.utcnow() - timedelta(minutes=2))
