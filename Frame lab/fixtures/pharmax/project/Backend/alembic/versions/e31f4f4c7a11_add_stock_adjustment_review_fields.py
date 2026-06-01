"""add stock adjustment review fields

Revision ID: e31f4f4c7a11
Revises: 6d24f45c2c01
Create Date: 2026-03-09 23:25:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "e31f4f4c7a11"
down_revision: Union[str, Sequence[str], None] = "6d24f45c2c01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


STOCK_ADJUSTMENT_STATUS_ENUM = postgresql.ENUM(
    "PENDING",
    "APPROVED",
    "REJECTED",
    name="stockadjustmentstatus",
    create_type=False,
)


def _is_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def _enum_type(pg_enum: postgresql.ENUM) -> sa.types.TypeEngine:
    if _is_postgresql():
        return pg_enum
    return sa.Enum(*pg_enum.enums, name=pg_enum.name)


def upgrade() -> None:
    if _is_postgresql():
        STOCK_ADJUSTMENT_STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "stock_adjustments",
        sa.Column("status", _enum_type(STOCK_ADJUSTMENT_STATUS_ENUM), nullable=False, server_default="APPROVED"),
    )
    op.add_column("stock_adjustments", sa.Column("approved_by_user_id", sa.String(length=36), nullable=True))
    op.add_column("stock_adjustments", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("stock_adjustments", sa.Column("approval_note", sa.String(length=255), nullable=True))
    op.create_index("ix_stock_adjustments_status", "stock_adjustments", ["status"], unique=False)
    op.create_foreign_key(
        "fk_stock_adjustments_approved_by_user_id_users",
        "stock_adjustments",
        "users",
        ["approved_by_user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_stock_adjustments_approved_by_user_id_users", "stock_adjustments", type_="foreignkey")
    op.drop_index("ix_stock_adjustments_status", table_name="stock_adjustments")
    op.drop_column("stock_adjustments", "approval_note")
    op.drop_column("stock_adjustments", "approved_at")
    op.drop_column("stock_adjustments", "approved_by_user_id")
    op.drop_column("stock_adjustments", "status")
    if _is_postgresql():
        STOCK_ADJUSTMENT_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
