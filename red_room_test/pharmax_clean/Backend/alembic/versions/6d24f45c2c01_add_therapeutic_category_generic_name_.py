"""add therapeutic_category generic_name payment_method dispensed_status

Revision ID: 6d24f45c2c01
Revises: a1b2c3d4e5f6
Create Date: 2026-02-19 17:58:44.329084

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "6d24f45c2c01"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PAYMENT_METHOD_ENUM = postgresql.ENUM(
    "CASH",
    "CARD",
    "BANK_TRANSFER",
    name="paymentmethod",
    create_type=False,
)
THERAPEUTIC_CATEGORY_ENUM = postgresql.ENUM(
    "ANALGESIC",
    "ANTI_MALARIAL",
    "ANTIBIOTIC",
    "ANTI_FUNGAL",
    "ANTI_INFLAMMATORY",
    "ANTI_DIARRHOEAL",
    "ANTACID",
    "ANTIHISTAMINE",
    "ANTIHYPERTENSIVE",
    "ANTI_DIABETIC",
    "COUGH_AND_COLD",
    "VITAMIN_SUPPLEMENT",
    "SKIN_CARE",
    "EYE_EAR_NOSE",
    "GASTROINTESTINAL",
    "CONTRACEPTIVE",
    "OTHER",
    name="therapeuticcategory",
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
        bind = op.get_bind()
        PAYMENT_METHOD_ENUM.create(bind, checkfirst=True)
        THERAPEUTIC_CATEGORY_ENUM.create(bind, checkfirst=True)

    op.add_column("invoices", sa.Column("finalized_by_id", sa.String(length=36), nullable=True))
    op.add_column("invoices", sa.Column("dispensed_by_id", sa.String(length=36), nullable=True))
    op.add_column("invoices", sa.Column("payment_method", _enum_type(PAYMENT_METHOD_ENUM), nullable=True))
    op.add_column("invoices", sa.Column("total_amount", sa.Numeric(10, 5), nullable=True))
    op.add_column("invoices", sa.Column("finalized_at", sa.DateTime(), nullable=True))
    op.add_column("invoices", sa.Column("dispensed_at", sa.DateTime(), nullable=True))
    op.add_column("products", sa.Column("generic_name", sa.String(length=255), nullable=True))
    op.add_column(
        "products",
        sa.Column("therapeutic_category", _enum_type(THERAPEUTIC_CATEGORY_ENUM), nullable=True),
    )
    op.create_index(op.f("ix_products_generic_name"), "products", ["generic_name"], unique=False)
    op.create_index(op.f("ix_products_therapeutic_category"), "products", ["therapeutic_category"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_products_therapeutic_category"), table_name="products")
    op.drop_index(op.f("ix_products_generic_name"), table_name="products")
    op.drop_column("products", "therapeutic_category")
    op.drop_column("products", "generic_name")
    op.drop_column("invoices", "dispensed_at")
    op.drop_column("invoices", "finalized_at")
    op.drop_column("invoices", "total_amount")
    op.drop_column("invoices", "payment_method")
    op.drop_column("invoices", "dispensed_by_id")
    op.drop_column("invoices", "finalized_by_id")
    if _is_postgresql():
        bind = op.get_bind()
        THERAPEUTIC_CATEGORY_ENUM.drop(bind, checkfirst=True)
        PAYMENT_METHOD_ENUM.drop(bind, checkfirst=True)
