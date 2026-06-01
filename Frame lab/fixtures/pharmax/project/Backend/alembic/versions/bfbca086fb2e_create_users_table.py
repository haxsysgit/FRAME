"""create users table

Revision ID: bfbca086fb2e
Revises: 883315fd2f64
Create Date: 2025-12-30 12:06:03.312523

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "bfbca086fb2e"
down_revision: Union[str, Sequence[str], None] = "883315fd2f64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


USER_ROLE_ENUM = postgresql.ENUM(
    "ADMIN",
    "CASHIER",
    "STAFF",
    name="user_role",
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
        USER_ROLE_ENUM.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", _enum_type(USER_ROLE_ENUM), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    if _is_postgresql():
        USER_ROLE_ENUM.drop(op.get_bind(), checkfirst=True)
