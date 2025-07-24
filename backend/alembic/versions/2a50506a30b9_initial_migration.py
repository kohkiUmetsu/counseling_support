"""Initial migration

Revision ID: 2a50506a30b9
Revises: 
Create Date: 2025-07-24 16:48:20.089717

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a50506a30b9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # counseling_sessions テーブルの作成
    op.create_table(
        'counseling_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('audio_file_url', sa.Text(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('result', sa.String(50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # transcriptions テーブルの作成
    op.create_table(
        'transcriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('counseling_sessions.id'), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('speaker_segments', postgresql.JSONB(), nullable=True),
        sa.Column('processing_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('language', sa.String(10), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('transcriptions')
    op.drop_table('counseling_sessions')