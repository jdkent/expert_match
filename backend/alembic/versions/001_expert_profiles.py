"""Create expert profile tables.

Revision ID: 001_expert_profiles
Revises:
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa


revision = "001_expert_profiles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "expert_profiles",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False, unique=True),
        sa.Column("orcid_id", sa.String(length=19), nullable=True, unique=True),
        sa.Column("website_url", sa.String(length=512), nullable=True),
        sa.Column("x_handle", sa.String(length=128), nullable=True),
        sa.Column("linkedin_identifier", sa.String(length=255), nullable=True),
        sa.Column("bluesky_identifier", sa.String(length=255), nullable=True),
        sa.Column("github_handle", sa.String(length=255), nullable=True),
        sa.Column("email_verification_status", sa.String(length=32), nullable=False),
        sa.Column("orcid_validation_status", sa.String(length=32), nullable=False),
        sa.Column("discoverability_status", sa.String(length=64), nullable=False),
        sa.Column("verification_token_hash", sa.String(length=128), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "expert_availability_slots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("canonical_slot_id", sa.String(), nullable=False),
        sa.Column("slot_start_at", sa.DateTime(), nullable=False),
        sa.Column("slot_end_at", sa.DateTime(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.Column("local_start_time", sa.Time(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column("attendee_request_count", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("expert_availability_slots")
    op.drop_table("expert_profiles")
