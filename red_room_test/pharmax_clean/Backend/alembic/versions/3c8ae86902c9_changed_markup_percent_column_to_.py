"""Changed markup_percent column to Numeric type for accuracy

Revision ID: 3c8ae86902c9
Revises: e31f4f4c7a11
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "3c8ae86902c9"
down_revision = "1a1aaf069c14"
branch_labels = None
depends_on = None


def upgrade():
    # Batch alter keeps this safe across supported database engines.
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "markup_percent",
            existing_type=sa.FLOAT(),
            type_=sa.Numeric(10, 2),
            existing_nullable=True,
        )


def downgrade():
    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column(
            "markup_percent",
            existing_type=sa.Numeric(10, 2),
            type_=sa.FLOAT(),
            existing_nullable=True,
        )
