"""add hashed_pin column and normalize role values

Revision ID: a1b2c3d4e5f6
Revises: c874736105a3
Create Date: 2026-02-14 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "c874736105a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgresql() -> bool:
    return op.get_context().dialect.name == "postgresql"


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("users", "hashed_pin"):
        op.add_column("users", sa.Column("hashed_pin", sa.String(length=255), nullable=True))

    if _is_postgresql():
        op.execute(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'SALES'
              ) AND NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'STAFF'
              ) THEN
                ALTER TYPE user_role RENAME VALUE 'SALES' TO 'STAFF';
              END IF;
            END
            $$;
            """
        )
    else:
        op.execute("UPDATE users SET role = 'STAFF' WHERE role = 'SALES'")


def downgrade() -> None:
    if _is_postgresql():
        op.execute(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'STAFF'
              ) AND NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_enum e ON e.enumtypid = t.oid
                WHERE t.typname = 'user_role' AND e.enumlabel = 'SALES'
              ) THEN
                ALTER TYPE user_role RENAME VALUE 'STAFF' TO 'SALES';
              END IF;
            END
            $$;
            """
        )
    else:
        op.execute("UPDATE users SET role = 'SALES' WHERE role = 'STAFF'")

    if _has_column("users", "hashed_pin"):
        op.drop_column("users", "hashed_pin")
