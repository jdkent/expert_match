"""Replace verification and edit sessions with persistent expert access keys.

Revision ID: 005_expert_access_keys
Revises: 004_pgvector_embeddings
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa


revision = "005_expert_access_keys"
down_revision = "004_pgvector_embeddings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("expert_profiles", sa.Column("access_key_hash", sa.String(length=128), nullable=True))
    op.create_index(
        "ix_expert_profiles_access_key_hash",
        "expert_profiles",
        ["access_key_hash"],
        unique=True,
    )
    op.execute(
        "UPDATE expert_profiles "
        "SET discoverability_status = 'pending_enrichment' "
        "WHERE discoverability_status = 'pending_email_verification'"
    )
    op.drop_table("expert_edit_sessions")
    op.drop_column("expert_profiles", "email_verification_status")
    op.drop_column("expert_profiles", "verification_token_hash")
    op.drop_column("expert_profiles", "verified_at")


def downgrade() -> None:
    op.add_column("expert_profiles", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("expert_profiles", sa.Column("verification_token_hash", sa.String(length=128), nullable=True))
    op.add_column(
        "expert_profiles",
        sa.Column("email_verification_status", sa.String(length=32), nullable=False, server_default="pending"),
    )
    op.create_table(
        "expert_edit_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_expert_edit_sessions_expert_profile_id", "expert_edit_sessions", ["expert_profile_id"])
    op.create_index("ix_expert_edit_sessions_token_hash", "expert_edit_sessions", ["token_hash"], unique=True)
    op.drop_index("ix_expert_profiles_access_key_hash", table_name="expert_profiles")
    op.drop_column("expert_profiles", "access_key_hash")

