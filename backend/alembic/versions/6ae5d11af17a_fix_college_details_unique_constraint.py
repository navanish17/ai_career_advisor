"""fix_college_details_unique_constraint

Revision ID: 6ae5d11af17a
Revises: 00e4640dbaf5
Create Date: 2025-12-29 23:44:20.892151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae5d11af17a'
down_revision: Union[str, Sequence[str], None] = '00e4640dbaf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # SQLite doesn't support DROP CONSTRAINT directly
    # So we need to recreate the table
    
    # Step 1: Rename old table
    op.rename_table('college_details', 'college_details_old')
    
    # Step 2: Create new table with correct constraint
    op.create_table(
        'college_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('college_id', sa.Integer(), nullable=False),
        sa.Column('degree', sa.String(100), nullable=False),
        sa.Column('branch', sa.String(100), nullable=False),
        sa.Column('fees_value', sa.String(100), nullable=True),
        sa.Column('fees_source', sa.String(500), nullable=True),
        sa.Column('fees_extracted_text', sa.String(1000), nullable=True),
        sa.Column('avg_package_value', sa.String(100), nullable=True),
        sa.Column('avg_package_source', sa.String(500), nullable=True),
        sa.Column('avg_package_extracted_text', sa.String(1000), nullable=True),
        sa.Column('highest_package_value', sa.String(100), nullable=True),
        sa.Column('highest_package_source', sa.String(500), nullable=True),
        sa.Column('highest_package_extracted_text', sa.String(1000), nullable=True),
        sa.Column('entrance_exam_value', sa.String(100), nullable=True),
        sa.Column('entrance_exam_source', sa.String(500), nullable=True),
        sa.Column('entrance_exam_extracted_text', sa.String(1000), nullable=True),
        sa.Column('cutoff_value', sa.String(200), nullable=True),
        sa.Column('cutoff_source', sa.String(500), nullable=True),
        sa.Column('cutoff_extracted_text', sa.String(1000), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('college_id', 'degree', 'branch', name='uq_college_degree_branch')
    )
    
    # Step 3: Copy data from old table
    op.execute("""
        INSERT INTO college_details 
        SELECT * FROM college_details_old
    """)
    
    # Step 4: Drop old table
    op.drop_table('college_details_old')


def downgrade():
    # Reverse the process if needed
    pass

