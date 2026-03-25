"""Create matching and outreach tables.

Revision ID: 002_matching_and_outreach
Revises: 001_expert_profiles
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa


revision = "002_matching_and_outreach"
down_revision = "001_expert_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "expert_queries",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("requester_contact_id", sa.String(), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("query_embedding_vector", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(length=255), nullable=False),
        sa.Column("similarity_threshold", sa.Float(), nullable=False),
        sa.Column("search_status", sa.String(length=32), nullable=False),
    )
    op.create_table(
        "outreach_requests",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_query_id", sa.String(), nullable=False),
        sa.Column("requester_contact_id", sa.String(), nullable=False),
        sa.Column("primary_expert_profile_id", sa.String(), nullable=False),
        sa.Column("message_subject", sa.String(length=255), nullable=False),
        sa.Column("message_body", sa.Text(), nullable=False),
        sa.Column("overall_status", sa.String(length=32), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("outreach_requests")
    op.drop_table("expert_queries")
