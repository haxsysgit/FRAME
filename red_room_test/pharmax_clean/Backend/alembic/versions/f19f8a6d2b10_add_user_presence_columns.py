"""add user presence timestamp columns

Revision ID: f19f8a6d2b10
Revises: a6f92b1d3e44
Create Date: 2026-04-08 22:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f19f8a6d2b10"
down_revision: Union[str, Sequence[str], None] = "a6f92b1d3e44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return inspector.has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_table("users"):
        return

    if not _has_column("users", "last_login_at"):
        op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    if not _has_column("users", "last_seen_at"):
        op.add_column("users", sa.Column("last_seen_at", sa.DateTime(), nullable=True))
    if not _has_column("users", "last_logout_at"):
        op.add_column("users", sa.Column("last_logout_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    if not _has_table("users"):
        return

    if _has_column("users", "last_logout_at"):
        op.drop_column("users", "last_logout_at")
    if _has_column("users", "last_seen_at"):
        op.drop_column("users", "last_seen_at")
    if _has_column("users", "last_login_at"):
        op.drop_column("users", "last_login_at")
