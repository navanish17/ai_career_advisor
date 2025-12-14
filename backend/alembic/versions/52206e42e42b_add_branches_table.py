"""add branches table + change duration_years to float

Revision ID: 52206e42e42b
Revises: 78fd74dae51f
Create Date: 2025-12-14 16:30:07.206050
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "52206e42e42b"
down_revision: Union[str, Sequence[str], None] = "78fd74dae51f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1️⃣ Create branches table
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("degree_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["degree_id"], ["degrees.id"], ondelete="CASCADE"
        ),
    )

    op.create_index("ix_branches_id", "branches", ["id"])
    op.create_index("ix_branches_name", "branches", ["name"])

    # 2️⃣ SQLite-safe column type change
    with op.batch_alter_table("degrees") as batch_op:
        batch_op.alter_column(
            "duration_years",
            existing_type=sa.INTEGER(),
            type_=sa.Float(),
            existing_nullable=True,
        )


def downgrade() -> None:
    """Downgrade schema."""

    with op.batch_alter_table("degrees") as batch_op:
        batch_op.alter_column(
            "duration_years",
            existing_type=sa.Float(),
            type_=sa.INTEGER(),
            existing_nullable=True,
        )

    op.drop_index("ix_branches_name", table_name="branches")
    op.drop_index("ix_branches_id", table_name="branches")
    op.drop_table("branches")
