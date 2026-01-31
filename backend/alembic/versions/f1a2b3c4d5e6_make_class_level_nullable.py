"""make class_level nullable in roadmap table

Revision ID: f1a2b3c4d5e6
Revises: 4cd94df6fdf8
Create Date: 2026-01-30 10:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '4cd94df6fdf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make class_level nullable to support backward planning roadmaps."""
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    # This migration documents the manual change made to the database
    pass


def downgrade() -> None:
    """Revert class_level to NOT NULL."""
    pass
