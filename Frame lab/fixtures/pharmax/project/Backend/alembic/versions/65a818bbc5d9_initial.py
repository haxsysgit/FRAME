"""initial

Revision ID: 65a818bbc5d9
Revises:
Create Date: 2025-12-15 13:36:16.145864

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "65a818bbc5d9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PRODUCT_TYPE_ENUM = postgresql.ENUM(
    "MEDICAL",
    "NON_MEDICAL",
    name="producttype",
    create_type=False,
)
PRODUCT_STATUS_ENUM = postgresql.ENUM(
    "ACTIVE",
    "DELETED",
    "INACTIVE",
    name="productstatus",
    create_type=False,
)
STOCK_ADJUSTMENT_REASON_ENUM = postgresql.ENUM(
    "INITIAL_IMPORT",
    "MANUAL_ADJUSTMENT",
    name="stockadjustmentreason",
    create_type=False,
)


def _is_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def _create_enums() -> None:
    if _is_postgresql():
        bind = op.get_bind()
        PRODUCT_TYPE_ENUM.create(bind, checkfirst=True)
        PRODUCT_STATUS_ENUM.create(bind, checkfirst=True)
        STOCK_ADJUSTMENT_REASON_ENUM.create(bind, checkfirst=True)


def _drop_enums() -> None:
    if _is_postgresql():
        bind = op.get_bind()
        STOCK_ADJUSTMENT_REASON_ENUM.drop(bind, checkfirst=True)
        PRODUCT_STATUS_ENUM.drop(bind, checkfirst=True)
        PRODUCT_TYPE_ENUM.drop(bind, checkfirst=True)


def _enum_type(pg_enum: postgresql.ENUM) -> sa.types.TypeEngine:
    if _is_postgresql():
        return pg_enum
    return sa.Enum(*pg_enum.enums, name=pg_enum.name)


def upgrade() -> None:
    """Upgrade schema."""
    _create_enums()

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("sku", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=True),
        sa.Column("supplier_name", sa.String(length=255), nullable=True),
        sa.Column("barcode", sa.String(length=255), nullable=True),
        sa.Column("markup_percent", sa.Float(), nullable=True),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=False),
        sa.Column("reorder_level", sa.Integer(), nullable=False),
        sa.Column("product_type", _enum_type(PRODUCT_TYPE_ENUM), nullable=False),
        sa.Column("dispense_without_prescription", sa.Boolean(), nullable=False),
        sa.Column("return_policy", sa.String(length=255), nullable=True),
        sa.Column("status", _enum_type(PRODUCT_STATUS_ENUM), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_barcode"), "products", ["barcode"], unique=False)
    op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)

    op.create_table(
        "stock_adjustments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("change_qty", sa.Integer(), nullable=False),
        sa.Column("reason", _enum_type(STOCK_ADJUSTMENT_REASON_ENUM), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=True),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stock_adjustments_product_id"), "stock_adjustments", ["product_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_stock_adjustments_product_id"), table_name="stock_adjustments")
    op.drop_table("stock_adjustments")
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_barcode"), table_name="products")
    op.drop_table("products")
    _drop_enums()
