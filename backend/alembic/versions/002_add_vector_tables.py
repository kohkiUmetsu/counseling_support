"""Add vector tables and pgvector extension

Revision ID: 002
Revises: 001
Create Date: 2024-07-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # pgvector拡張の有効化
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')
    
    # success_conversation_vectors テーブルの作成
    op.create_table(
        'success_conversation_vectors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('counseling_sessions.id'), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # cluster_results テーブルの作成
    op.create_table(
        'cluster_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('algorithm', sa.Text(), nullable=False),
        sa.Column('cluster_count', sa.Integer(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('silhouette_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # cluster_assignments テーブルの作成
    op.create_table(
        'cluster_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('success_conversation_vectors.id'), nullable=False),
        sa.Column('cluster_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cluster_results.id'), nullable=False),
        sa.Column('cluster_label', sa.Integer(), nullable=False),
        sa.Column('distance_to_centroid', sa.Float(), nullable=True)
    )
    
    # cluster_representatives テーブルの作成
    op.create_table(
        'cluster_representatives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('cluster_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cluster_results.id'), nullable=False),
        sa.Column('vector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('success_conversation_vectors.id'), nullable=False),
        sa.Column('cluster_label', sa.Integer(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('distance_to_centroid', sa.Float(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # anomaly_detection_results テーブルの作成
    op.create_table(
        'anomaly_detection_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('vector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('success_conversation_vectors.id'), nullable=False),
        sa.Column('algorithm', sa.Text(), nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=False),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )
    
    # インデックスの作成
    # ベクトル検索用のIVFFLATインデックス
    op.execute("""
        CREATE INDEX ON success_conversation_vectors 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)
    
    # その他のインデックス
    op.create_index('ix_success_conversation_vectors_session_id', 'success_conversation_vectors', ['session_id'])
    op.create_index('ix_cluster_assignments_cluster_result_id', 'cluster_assignments', ['cluster_result_id'])
    op.create_index('ix_cluster_assignments_cluster_label', 'cluster_assignments', ['cluster_label'])
    op.create_index('ix_cluster_representatives_cluster_result_id', 'cluster_representatives', ['cluster_result_id'])
    op.create_index('ix_cluster_representatives_is_primary', 'cluster_representatives', ['is_primary'])


def downgrade():
    # インデックスの削除
    op.drop_index('ix_cluster_representatives_is_primary', 'cluster_representatives')
    op.drop_index('ix_cluster_representatives_cluster_result_id', 'cluster_representatives')
    op.drop_index('ix_cluster_assignments_cluster_label', 'cluster_assignments')
    op.drop_index('ix_cluster_assignments_cluster_result_id', 'cluster_assignments')
    op.drop_index('ix_success_conversation_vectors_session_id', 'success_conversation_vectors')
    
    # ベクトル検索インデックスの削除
    op.execute("DROP INDEX IF EXISTS success_conversation_vectors_embedding_idx;")
    
    # テーブルの削除
    op.drop_table('anomaly_detection_results')
    op.drop_table('cluster_representatives')
    op.drop_table('cluster_assignments')
    op.drop_table('cluster_results')
    op.drop_table('success_conversation_vectors')
    
    # pgvector拡張の削除（慎重に）
    # op.execute('DROP EXTENSION IF EXISTS vector;')