"""Add product units and base unit

Revision ID: d87dfafd3560
Revises: 65a818bbc5d9
Create Date: 2025-12-17 09:08:01.632345

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d87dfafd3560"
down_revision: Union[str, Sequence[str], None] = "65a818bbc5d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


BASE_UNIT_ENUM = postgresql.ENUM(
    "TABLET",
    "CAPSULE",
    "SACHET",
    "PACK",
    "BOTTLE",
    "VIAL",
    "AMPOULE",
    "TUBE",
    "CREAM",
    "OINTMENT",
    "GEL",
    "SYRUP",
    "SUSPENSION",
    "DROPS",
    "POWDER",
    "BOX",
    "STRIP",
    "CARTON",
    "CONTAINER",
    name="baseunit",
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
        BASE_UNIT_ENUM.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "product_units",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("name", _enum_type(BASE_UNIT_ENUM), nullable=False),
        sa.Column("multiplier_to_base", sa.Integer(), nullable=False),
        sa.Column("price_per_unit", sa.Float(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_units_product_id"), "product_units", ["product_id"], unique=False)
    op.add_column(
        "products",
        sa.Column("base_unit", _enum_type(BASE_UNIT_ENUM), nullable=False, server_default="PACK"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "base_unit")
    op.drop_index(op.f("ix_product_units_product_id"), table_name="product_units")
    op.drop_table("product_units")
    if _is_postgresql():
        BASE_UNIT_ENUM.drop(op.get_bind(), checkfirst=True)
