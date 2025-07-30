"""enable pgvector extension

Revision ID: enable_pgvector
Revises: fix_transcriptions_id_type
Create Date: 2025-07-28 19:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'enable_pgvector'
down_revision = 'fix_transcriptions_id_type'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')


def downgrade() -> None:
    # Disable pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')