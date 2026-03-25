"""Add a manual-expertise-only HNSW index for backend-configured search filtering.

Revision ID: 006_manual_expertise_hnsw_index
Revises: 005_expert_access_keys
Create Date: 2026-03-24
"""

from alembic import op


revision = "006_manual_expertise_hnsw_index"
down_revision = "005_expert_access_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_manual_embedding_vector_hnsw
        ON expert_search_documents
        USING hnsw (embedding_vector vector_cosine_ops)
        WHERE source_type = 'manual_expertise' AND is_active = true
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_manual_embedding_vector_hnsw")
