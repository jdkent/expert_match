"""Drop obsolete trigram index and extension after lexical search refactor.

Revision ID: 010_drop_pg_trgm_cleanup
Revises: 009_postgres_fts_trgm_indexes
Create Date: 2026-03-25
"""

from alembic import op


revision = "010_drop_pg_trgm_cleanup"
down_revision = "009_postgres_fts_trgm_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_document_text_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")


def downgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_document_text_trgm
        ON expert_search_documents
        USING gin (lower(document_text) gin_trgm_ops)
        WHERE is_active = true
        """
    )
