"""add invoice cashier_note column

Revision ID: 6f04d1bc9e37
Revises: f19f8a6d2b10
Create Date: 2026-04-08 23:55:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f04d1bc9e37"
down_revision: Union[str, Sequence[str], None] = "f19f8a6d2b10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return inspector.has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_table("invoices"):
        return

    if not _has_column("invoices", "cashier_note"):
        op.add_column("invoices", sa.Column("cashier_note", sa.String(length=500), nullable=True))


def downgrade() -> None:
    if not _has_table("invoices"):
        return

    if _has_column("invoices", "cashier_note"):
        op.drop_column("invoices", "cashier_note")
