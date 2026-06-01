"""merge heads

Revision ID: 2fefb74fd050
Revises: e31f4f4c7a11, 3c8ae86902c9
Create Date: 2026-03-27 00:02:10.173075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fefb74fd050'
down_revision: Union[str, Sequence[str], None] = ('e31f4f4c7a11', '3c8ae86902c9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
