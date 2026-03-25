"""Add PostgreSQL full-text and trigram indexes for expert search documents.

Revision ID: 009_postgres_fts_trgm_indexes
Revises: 008_expert_profile_short_bio
Create Date: 2026-03-25
"""

from alembic import op


revision = "009_postgres_fts_trgm_indexes"
down_revision = "008_expert_profile_short_bio"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_document_text_bm25")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_document_text_tsvector
        ON expert_search_documents
        USING gin (to_tsvector('english', coalesce(document_text, '')))
        WHERE is_active = true
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_document_text_trgm
        ON expert_search_documents
        USING gin (lower(document_text) gin_trgm_ops)
        WHERE is_active = true
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_document_text_trgm")
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_document_text_tsvector")
