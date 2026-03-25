"""Store embeddings in pgvector columns and add cosine index.

Revision ID: 004_pgvector_embeddings
Revises: 003_runtime_service_tables
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa


revision = "004_pgvector_embeddings"
down_revision = "003_runtime_service_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        ALTER TABLE expert_search_documents
        ALTER COLUMN embedding_vector TYPE vector(768)
        USING embedding_vector::vector(768)
        """
    )
    op.execute(
        """
        ALTER TABLE expert_queries
        ALTER COLUMN query_embedding_vector TYPE vector(768)
        USING query_embedding_vector::vector(768)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_embedding_vector_hnsw
        ON expert_search_documents
        USING hnsw (embedding_vector vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_embedding_vector_hnsw")
    op.alter_column(
        "expert_queries",
        "query_embedding_vector",
        existing_type=sa.NullType(),
        type_=sa.Text(),
        postgresql_using="query_embedding_vector::text",
    )
    op.alter_column(
        "expert_search_documents",
        "embedding_vector",
        existing_type=sa.NullType(),
        type_=sa.Text(),
        postgresql_using="embedding_vector::text",
    )
