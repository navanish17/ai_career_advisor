"""change duration_years to float

Revision ID: 78fd74dae51f
Revises: 5cda92213c2b
Create Date: 2025-12-13 17:26:04.308671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78fd74dae51f'
down_revision: Union[str, Sequence[str], None] = '5cda92213c2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
