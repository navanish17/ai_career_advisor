"""add stream to profile

Revision ID: 5b7c357e7c10
Revises: 6a531e7f2fb9
Create Date: 2025-12-25 11:12:16.435455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b7c357e7c10'
down_revision: Union[str, Sequence[str], None] = '6a531e7f2fb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column("stream", sa.String(length=50), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("profiles", "stream")

