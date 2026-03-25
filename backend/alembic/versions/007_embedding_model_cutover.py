"""Track embedding backfills and scope HNSW indexes to the active target model.

Revision ID: 007_embedding_model_cutover
Revises: 006_manual_expertise_hnsw_index
Create Date: 2026-03-25
"""

from alembic import op
import sqlalchemy as sa


revision = "007_embedding_model_cutover"
down_revision = "006_manual_expertise_hnsw_index"
branch_labels = None
depends_on = None

LEGACY_MODEL = "allenai/specter2"
TARGET_MODEL = "sentence-transformers/all-mpnet-base-v2"


def upgrade() -> None:
    op.create_table(
        "backfill_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("target_embedding_model", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "target_embedding_model", name="uq_backfill_runs_name_model"),
    )
    op.create_index("ix_backfill_runs_name", "backfill_runs", ["name"])

    op.execute(
        f"""
        UPDATE expert_search_documents
        SET embedding_model = '{LEGACY_MODEL}'
        WHERE embedding_model IS DISTINCT FROM '{TARGET_MODEL}'
        """
    )
    op.execute(
        f"""
        UPDATE expert_queries
        SET embedding_model = '{LEGACY_MODEL}'
        WHERE embedding_model IS DISTINCT FROM '{TARGET_MODEL}'
        """
    )

    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_embedding_vector_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_manual_embedding_vector_hnsw")
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_current_embedding_vector_hnsw
        ON expert_search_documents
        USING hnsw (embedding_vector vector_cosine_ops)
        WHERE is_active = true AND embedding_model = '{TARGET_MODEL}'
        """
    )
    op.execute(
        f"""
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_current_manual_embedding_vector_hnsw
        ON expert_search_documents
        USING hnsw (embedding_vector vector_cosine_ops)
        WHERE source_type = 'manual_expertise'
          AND is_active = true
          AND embedding_model = '{TARGET_MODEL}'
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_current_manual_embedding_vector_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_expert_search_documents_current_embedding_vector_hnsw")
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_embedding_vector_hnsw
        ON expert_search_documents
        USING hnsw (embedding_vector vector_cosine_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_expert_search_documents_manual_embedding_vector_hnsw
        ON expert_search_documents
        USING hnsw (embedding_vector vector_cosine_ops)
        WHERE source_type = 'manual_expertise' AND is_active = true
        """
    )
    op.drop_index("ix_backfill_runs_name", table_name="backfill_runs")
    op.drop_table("backfill_runs")
