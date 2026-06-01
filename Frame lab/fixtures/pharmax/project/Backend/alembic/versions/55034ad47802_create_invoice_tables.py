"""Create invoice tables

Revision ID: 55034ad47802
Revises: 04383611fec3
Create Date: 2025-12-17 10:05:09.028211

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "55034ad47802"
down_revision: Union[str, Sequence[str], None] = "04383611fec3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INVOICE_STATUS_ENUM = postgresql.ENUM(
    "DRAFT",
    "FINALIZED",
    "DISPENSED",
    "CANCELLED",
    name="invoicestatus",
    create_type=False,
)


def _is_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def _enum_type(pg_enum: postgresql.ENUM) -> sa.types.TypeEngine:
    if _is_postgresql():
        return pg_enum
    return sa.Enum(*pg_enum.enums, name=pg_enum.name)


def upgrade() -> None:
    """Upgrade schema."""
    if _is_postgresql():
        INVOICE_STATUS_ENUM.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "invoices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sold_by_name", sa.String(length=100), nullable=True),
        sa.Column("status", _enum_type(INVOICE_STATUS_ENUM), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "invoice_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("invoice_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("product_unit_id", sa.String(length=36), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 5), nullable=False),
        sa.Column("line_total", sa.Numeric(10, 5), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["product_unit_id"], ["product_units.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_items_invoice_id"), "invoice_items", ["invoice_id"], unique=False)
    op.create_index(op.f("ix_invoice_items_product_id"), "invoice_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_invoice_items_product_unit_id"), "invoice_items", ["product_unit_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_invoice_items_product_unit_id"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_product_id"), table_name="invoice_items")
    op.drop_index(op.f("ix_invoice_items_invoice_id"), table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_table("invoices")
    if _is_postgresql():
        INVOICE_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
