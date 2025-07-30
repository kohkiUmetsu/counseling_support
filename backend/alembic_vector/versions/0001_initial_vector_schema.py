"""Initial vector database schema

Revision ID: 0001
Revises: 
Create Date: 2025-07-30 17:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create success_conversation_vectors table
    op.create_table('success_conversation_vectors',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.Text(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=False),
        sa.Column('chunk_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create cluster_results table
    op.create_table('cluster_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('algorithm', sa.Text(), nullable=False),
        sa.Column('cluster_count', sa.Integer(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('silhouette_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create cluster_assignments table
    op.create_table('cluster_assignments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vector_id', sa.UUID(), nullable=False),
        sa.Column('cluster_result_id', sa.UUID(), nullable=False),
        sa.Column('cluster_label', sa.Integer(), nullable=False),
        sa.Column('distance_to_centroid', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['cluster_result_id'], ['cluster_results.id'], ),
        sa.ForeignKeyConstraint(['vector_id'], ['success_conversation_vectors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create cluster_representatives table
    op.create_table('cluster_representatives',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('cluster_result_id', sa.UUID(), nullable=False),
        sa.Column('vector_id', sa.UUID(), nullable=False),
        sa.Column('cluster_label', sa.Integer(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('distance_to_centroid', sa.Float(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cluster_result_id'], ['cluster_results.id'], ),
        sa.ForeignKeyConstraint(['vector_id'], ['success_conversation_vectors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create anomaly_detection_results table
    op.create_table('anomaly_detection_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vector_id', sa.UUID(), nullable=False),
        sa.Column('algorithm', sa.Text(), nullable=False),
        sa.Column('anomaly_score', sa.Float(), nullable=False),
        sa.Column('is_anomaly', sa.Boolean(), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vector_id'], ['success_conversation_vectors.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('anomaly_detection_results')
    op.drop_table('cluster_representatives')
    op.drop_table('cluster_assignments')
    op.drop_table('cluster_results')
    op.drop_table('success_conversation_vectors')
    op.execute('DROP EXTENSION IF EXISTS vector')