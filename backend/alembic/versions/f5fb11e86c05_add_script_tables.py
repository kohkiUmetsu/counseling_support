"""Add script tables

Revision ID: f5fb11e86c05
Revises: b6c375a00ba9
Create Date: 2025-07-24 16:51:27.973111

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5fb11e86c05'
down_revision = 'b6c375a00ba9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # improvement_scripts テーブルの作成
    op.create_table(
        'improvement_scripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('version', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content', postgresql.JSONB(), nullable=False),
        sa.Column('generation_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('quality_metrics', postgresql.JSONB(), nullable=True),
        sa.Column('status', sa.Text(), default='draft'),
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('cluster_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cluster_results.id'), nullable=True),
        sa.Column('based_on_failure_sessions', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('activated_at', sa.DateTime(), nullable=True)
    )
    
    # script_usage_analytics テーブルの作成
    op.create_table(
        'script_usage_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('script_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('improvement_scripts.id'), nullable=False),
        sa.Column('usage_start_date', sa.DateTime(), nullable=False),
        sa.Column('usage_end_date', sa.DateTime(), nullable=True),
        sa.Column('total_sessions', sa.Integer(), default=0),
        sa.Column('successful_sessions', sa.Integer(), default=0),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('baseline_conversion_rate', sa.Float(), nullable=True),
        sa.Column('improvement_rate', sa.Float(), nullable=True),
        sa.Column('statistical_significance', sa.Boolean(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # インデックスの作成
    op.create_index('ix_improvement_scripts_status', 'improvement_scripts', ['status'])
    op.create_index('ix_improvement_scripts_is_active', 'improvement_scripts', ['is_active'])
    op.create_index('ix_improvement_scripts_created_at', 'improvement_scripts', ['created_at'])
    op.create_index('ix_script_usage_analytics_script_id', 'script_usage_analytics', ['script_id'])


def downgrade() -> None:
    # インデックスの削除
    op.drop_index('ix_script_usage_analytics_script_id', 'script_usage_analytics')
    op.drop_index('ix_improvement_scripts_created_at', 'improvement_scripts')
    op.drop_index('ix_improvement_scripts_is_active', 'improvement_scripts')
    op.drop_index('ix_improvement_scripts_status', 'improvement_scripts')
    
    # テーブルの削除  
    op.drop_table('script_usage_analytics')
    op.drop_table('improvement_scripts')