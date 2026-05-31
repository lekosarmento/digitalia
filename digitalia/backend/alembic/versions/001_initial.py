"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-30 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: learners
    op.create_table(
        'learners',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('phone_hash', sa.String(length=64), nullable=False),
        sa.Column('phone_encrypted', sa.LargeBinary(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.CHAR(length=2), nullable=True),
        sa.Column('current_trail', sa.String(length=50), nullable=True),
        sa.Column('current_state', sa.String(length=50), server_default='unknown', nullable=False),
        sa.Column('openai_assistant_id', sa.String(length=200), nullable=True),
        sa.Column('openai_thread_id', sa.String(length=200), nullable=True),
        sa.Column('level', sa.Integer(), server_default='1', nullable=False),
        sa.Column('completed_projects', sa.Integer(), server_default='0', nullable=False),
        sa.Column('avg_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('total_earned_brl', sa.Numeric(precision=10, scale=2), server_default='0.00', nullable=False),
        sa.Column('consent_given', sa.Boolean(), server_default='FALSE', nullable=False),
        sa.Column('consent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('parental_consent', sa.Boolean(), nullable=True),
        sa.Column('data_retention_until', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('anonymized_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone_hash'),
        sa.CheckConstraint('age >= 16', name='check_age')
    )

    # 2. Table: learner_skills
    op.create_table(
        'learner_skills',
        sa.Column('learner_id', sa.UUID(), nullable=False),
        sa.Column('skill', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Numeric(precision=4, scale=1), server_default='0.0', nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['learner_id'], ['learners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('learner_id', 'skill')
    )

    # 3. Table: completed_trails
    op.create_table(
        'completed_trails',
        sa.Column('learner_id', sa.UUID(), nullable=False),
        sa.Column('trail', sa.String(length=50), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('certificate_id', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['learners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('learner_id', 'trail')
    )

    # 4. Table: lesson_progress
    op.create_table(
        'lesson_progress',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('learner_id', sa.UUID(), nullable=False),
        sa.Column('trail', sa.String(length=50), nullable=True),
        sa.Column('lesson_id', sa.String(length=100), nullable=True),
        sa.Column('score', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True),
        sa.Column('attempts', sa.Integer(), server_default='1', nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['learner_id'], ['learners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. Table: companies
    op.create_table(
        'companies',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('cnpj', sa.String(length=14), nullable=True),
        sa.Column('contact_name', sa.String(length=200), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone_hash', sa.String(length=64), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.CHAR(length=2), nullable=True),
        sa.Column('avg_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('total_projects', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='FALSE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 6. Table: projects
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_trail', sa.String(length=50), nullable=True),
        sa.Column('required_skills', sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column('complexity', sa.Integer(), nullable=True),
        sa.Column('budget_brl', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('hours_needed', sa.Numeric(precision=4, scale=1), nullable=True),
        sa.Column('deadline_days', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='open', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('complexity BETWEEN 1 AND 10', name='check_complexity')
    )

    # 7. Table: project_matches
    op.create_table(
        'project_matches',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('learner_id', sa.UUID(), nullable=False),
        sa.Column('match_score', sa.Numeric(precision=5, scale=1), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='proposed', nullable=False),
        sa.Column('learner_rating', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('payment_id', sa.String(length=200), nullable=True),
        sa.Column('learner_earned_brl', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['learners.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. Table: certificates
    op.create_table(
        'certificates',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('learner_id', sa.UUID(), nullable=False),
        sa.Column('trail', sa.String(length=50), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('tx_hash', sa.String(length=200), nullable=True),
        sa.Column('contract_address', sa.String(length=200), nullable=True),
        sa.Column('token_id', sa.Integer(), nullable=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['learners.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('level BETWEEN 1 AND 3', name='check_cert_level')
    )

    # 9. Table: conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('learner_id', sa.UUID(), nullable=False),
        sa.Column('wa_message_id', sa.String(length=200), nullable=True),
        sa.Column('direction', sa.String(length=10), nullable=True),
        sa.Column('content_type', sa.String(length=20), server_default='text', nullable=False),
        sa.Column('content_encrypted', sa.LargeBinary(), nullable=True),
        sa.Column('openai_thread_id', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['learner_id'], ['learners.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("direction IN ('inbound', 'outbound')", name='check_direction')
    )


def downgrade() -> None:
    op.drop_table('conversations')
    op.drop_table('certificates')
    op.drop_table('project_matches')
    op.drop_table('projects')
    op.drop_table('companies')
    op.drop_table('lesson_progress')
    op.drop_table('completed_trails')
    op.drop_table('learner_skills')
    op.drop_table('learners')
