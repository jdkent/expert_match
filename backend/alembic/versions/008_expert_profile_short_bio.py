"""Add an optional short bio to expert profiles.

Revision ID: 008_expert_profile_short_bio
Revises: 007_embedding_model_cutover
Create Date: 2026-03-25
"""

from alembic import op
import sqlalchemy as sa


revision = "008_expert_profile_short_bio"
down_revision = "007_embedding_model_cutover"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("expert_profiles", sa.Column("short_bio", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("expert_profiles", "short_bio")
