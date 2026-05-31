"""Fix age constraint to include upper bound (age <= 30)

Revision ID: 002_fix_age_constraint
Revises: 001_initial
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = '002_fix_age_constraint'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Remove a constraint antiga
    op.drop_constraint('check_age', 'learners', type_='check')
    # Adiciona a constraint correta com limite superior
    op.create_check_constraint(
        'check_age_range',
        'learners',
        'age >= 16 AND age <= 30'
    )

def downgrade() -> None:
    op.drop_constraint('check_age_range', 'learners', type_='check')
    op.create_check_constraint(
        'check_age',
        'learners',
        'age >= 16'
    )
