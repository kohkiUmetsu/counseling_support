"""Add script management tables

Revision ID: 003
Revises: 002
Create Date: 2024-07-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
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
        sa.Column('counselor_performance', postgresql.JSONB(), nullable=True),
        sa.Column('time_period_analysis', postgresql.JSONB(), nullable=True),
        sa.Column('customer_segment_analysis', postgresql.JSONB(), nullable=True),
        sa.Column('statistical_significance', sa.Boolean(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('p_value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # script_feedback テーブルの作成
    op.create_table(
        'script_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('script_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('improvement_scripts.id'), nullable=False),
        sa.Column('counselor_name', sa.Text(), nullable=True),
        sa.Column('role', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('usability_score', sa.Integer(), nullable=True),
        sa.Column('effectiveness_score', sa.Integer(), nullable=True),
        sa.Column('positive_points', sa.Text(), nullable=True),
        sa.Column('improvement_suggestions', sa.Text(), nullable=True),
        sa.Column('specific_feedback', postgresql.JSONB(), nullable=True),
        sa.Column('usage_frequency', sa.Text(), nullable=True),
        sa.Column('usage_context', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # script_generation_jobs テーブルの作成
    op.create_table(
        'script_generation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', sa.Text(), unique=True, nullable=False),
        sa.Column('generation_config', postgresql.JSONB(), nullable=False),
        sa.Column('input_data', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.Text(), default='pending'),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('result_script_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('improvement_scripts.id'), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('token_usage', postgresql.JSONB(), nullable=True),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # script_versions テーブルの作成
    op.create_table(
        'script_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('script_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('improvement_scripts.id'), nullable=False),
        sa.Column('version_number', sa.Text(), nullable=False),
        sa.Column('parent_version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('script_versions.id'), nullable=True),
        sa.Column('content_snapshot', postgresql.JSONB(), nullable=False),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('change_details', postgresql.JSONB(), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('changed_by', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # script_templates テーブルの作成
    op.create_table(
        'script_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Text(), nullable=True),
        sa.Column('template_content', postgresql.JSONB(), nullable=False),
        sa.Column('is_public', sa.Boolean(), default=True),
        sa.Column('usage_count', sa.Integer(), default=0),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('target_scenarios', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # script_performance_metrics テーブルの作成
    op.create_table(
        'script_performance_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('script_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('improvement_scripts.id'), nullable=False),
        sa.Column('measurement_date', sa.DateTime(), nullable=False),
        sa.Column('measurement_period', sa.Text(), nullable=False),
        sa.Column('total_counseling_sessions', sa.Integer(), default=0),
        sa.Column('successful_conversions', sa.Integer(), default=0),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('baseline_conversion_rate', sa.Float(), nullable=True),
        sa.Column('improvement_percentage', sa.Float(), nullable=True),
        sa.Column('performance_by_counselor', postgresql.JSONB(), nullable=True),
        sa.Column('performance_by_time_slot', postgresql.JSONB(), nullable=True),
        sa.Column('performance_by_customer_type', postgresql.JSONB(), nullable=True),
        sa.Column('customer_satisfaction_score', sa.Float(), nullable=True),
        sa.Column('script_adherence_rate', sa.Float(), nullable=True),
        sa.Column('confidence_interval', postgresql.JSONB(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # インデックスの作成
    op.create_index('ix_improvement_scripts_status', 'improvement_scripts', ['status'])
    op.create_index('ix_improvement_scripts_is_active', 'improvement_scripts', ['is_active'])
    op.create_index('ix_improvement_scripts_created_at', 'improvement_scripts', ['created_at'])
    
    op.create_index('ix_script_usage_analytics_script_id', 'script_usage_analytics', ['script_id'])
    op.create_index('ix_script_feedback_script_id', 'script_feedback', ['script_id'])
    op.create_index('ix_script_generation_jobs_job_id', 'script_generation_jobs', ['job_id'])
    op.create_index('ix_script_generation_jobs_status', 'script_generation_jobs', ['status'])
    
    op.create_index('ix_script_versions_script_id', 'script_versions', ['script_id'])
    op.create_index('ix_script_performance_metrics_script_id', 'script_performance_metrics', ['script_id'])
    op.create_index('ix_script_performance_metrics_measurement_date', 'script_performance_metrics', ['measurement_date'])


def downgrade():
    # インデックスの削除
    op.drop_index('ix_script_performance_metrics_measurement_date', 'script_performance_metrics')
    op.drop_index('ix_script_performance_metrics_script_id', 'script_performance_metrics')
    op.drop_index('ix_script_versions_script_id', 'script_versions')
    
    op.drop_index('ix_script_generation_jobs_status', 'script_generation_jobs')
    op.drop_index('ix_script_generation_jobs_job_id', 'script_generation_jobs')
    op.drop_index('ix_script_feedback_script_id', 'script_feedback')
    op.drop_index('ix_script_usage_analytics_script_id', 'script_usage_analytics')
    
    op.drop_index('ix_improvement_scripts_created_at', 'improvement_scripts')
    op.drop_index('ix_improvement_scripts_is_active', 'improvement_scripts')
    op.drop_index('ix_improvement_scripts_status', 'improvement_scripts')
    
    # テーブルの削除
    op.drop_table('script_performance_metrics')
    op.drop_table('script_templates')
    op.drop_table('script_versions')
    op.drop_table('script_generation_jobs')
    op.drop_table('script_feedback')
    op.drop_table('script_usage_analytics')
    op.drop_table('improvement_scripts')