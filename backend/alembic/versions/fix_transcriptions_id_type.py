"""fix transcriptions id type

Revision ID: fix_transcriptions_id_type
Revises: 39d4bce4274a
Create Date: 2025-07-28 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_transcriptions_id_type'
down_revision = '39d4bce4274a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing transcriptions table and recreate with correct structure
    op.drop_table('transcriptions')
    
    # Recreate transcriptions table with String ID
    op.create_table('transcriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('segments', sa.JSON(), nullable=True),
        sa.Column('speaker_stats', sa.JSON(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['counseling_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop and recreate with old structure if needed
    op.drop_table('transcriptions')
    
    op.create_table('transcriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('speaker_segments', sa.JSON(), nullable=True),
        sa.Column('processing_metadata', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['counseling_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )