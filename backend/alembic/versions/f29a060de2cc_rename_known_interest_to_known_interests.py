"""rename known_interest to known_interests

Revision ID: f29a060de2cc
Revises: 39683362a425
Create Date: 2025-12-10 16:35:34.312192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'rename_known_interest_column'
down_revision = '39683362a425'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite has limited rename support, but this works for simple renames
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.alter_column(
            "known_interest",
            new_column_name="known_interests"
        )


def downgrade():
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.alter_column(
            "known_interests",
            new_column_name="known_interest"
        )
