"""Initial main database schema

Revision ID: 0001
Revises: 
Create Date: 2025-07-30 17:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create counseling_sessions table
    op.create_table('counseling_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('is_success', sa.Boolean(), nullable=True),
        sa.Column('counselor_name', sa.String(length=255), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('transcription_status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create transcriptions table
    op.create_table('transcriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=False),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='ja'),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('segments', sa.JSON(), nullable=True),
        sa.Column('speaker_stats', sa.JSON(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['counseling_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create transcription_segments table
    op.create_table('transcription_segments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('transcription_id', sa.String(length=36), nullable=False),
        sa.Column('segment_index', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('speaker', sa.String(length=20), nullable=True),
        sa.Column('speaker_confidence', sa.Float(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['transcription_id'], ['transcriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create improvement_scripts table
    op.create_table('improvement_scripts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('generation_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Text(), nullable=True, server_default='draft'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('cluster_result_id', sa.UUID(), nullable=True),  # No FK to vector DB
        sa.Column('based_on_failure_sessions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create other script-related tables...
    op.create_table('script_usage_analytics',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('script_id', sa.UUID(), nullable=False),
        sa.Column('usage_start_date', sa.DateTime(), nullable=False),
        sa.Column('usage_end_date', sa.DateTime(), nullable=True),
        sa.Column('total_sessions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('successful_sessions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('baseline_conversion_rate', sa.Float(), nullable=True),
        sa.Column('improvement_rate', sa.Float(), nullable=True),
        sa.Column('counselor_performance', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('time_period_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('customer_segment_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('statistical_significance', sa.Boolean(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['script_id'], ['improvement_scripts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('script_usage_analytics')
    op.drop_table('improvement_scripts')
    op.drop_table('transcription_segments')
    op.drop_table('transcriptions')
    op.drop_table('counseling_sessions')