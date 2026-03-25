"""Add runtime persistence tables and profile lifecycle columns.

Revision ID: 003_runtime_service_tables
Revises: 002_matching_and_outreach
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa


revision = "003_runtime_service_tables"
down_revision = "002_matching_and_outreach"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("expert_profiles", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("expert_queries", "requester_contact_id", existing_type=sa.String(), nullable=True)

    op.create_table(
        "expertise_entries",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("entry_text", sa.Text(), nullable=False),
        sa.Column("entry_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_expertise_entries_expert_profile_id", "expertise_entries", ["expert_profile_id"])

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

    op.create_table(
        "expert_enrichment_runs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("trigger_source", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("publication_selected_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("publication_embedded_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("availability_initialized", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_index("ix_expert_enrichment_runs_expert_profile_id", "expert_enrichment_runs", ["expert_profile_id"])

    op.create_table(
        "publication_records",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("external_work_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("publication_date", sa.Date(), nullable=True),
        sa.Column("author_position", sa.String(length=16), nullable=False),
        sa.Column("author_priority", sa.String(length=16), nullable=False),
        sa.Column("abstract_text", sa.Text(), nullable=True),
        sa.Column("abstract_status", sa.String(length=32), nullable=False),
        sa.Column("selected_for_enrichment", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_publication_records_expert_profile_id", "publication_records", ["expert_profile_id"])
    op.create_index("ix_publication_records_external_work_id", "publication_records", ["external_work_id"])

    op.create_table(
        "expert_search_documents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_record_id", sa.String(), nullable=False),
        sa.Column("document_text", sa.Text(), nullable=False),
        sa.Column("embedding_vector", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_expert_search_documents_expert_profile_id", "expert_search_documents", ["expert_profile_id"])
    op.create_index("ix_expert_search_documents_source_record_id", "expert_search_documents", ["source_record_id"])

    op.create_table(
        "requester_contacts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("organization", sa.Text(), nullable=True),
    )
    op.create_index("ix_requester_contacts_email", "requester_contacts", ["email"])

    op.create_table(
        "match_results",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("expert_query_id", sa.String(), nullable=False),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("expert_search_document_id", sa.String(), nullable=False),
        sa.Column("rank_position", sa.Integer(), nullable=False),
        sa.Column("expert_similarity_score", sa.Float(), nullable=False),
        sa.Column("top_document_similarity_score", sa.Float(), nullable=False),
        sa.Column("match_explanation", sa.Text(), nullable=True),
    )
    op.create_index("ix_match_results_expert_query_id", "match_results", ["expert_query_id"])
    op.create_index("ix_match_results_expert_profile_id", "match_results", ["expert_profile_id"])
    op.create_index("ix_match_results_expert_search_document_id", "match_results", ["expert_search_document_id"])

    op.create_table(
        "outreach_recipients",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("outreach_request_id", sa.String(), nullable=False),
        sa.Column("expert_profile_id", sa.String(), nullable=False),
        sa.Column("delivery_status", sa.String(length=32), nullable=False),
        sa.Column("delivery_reference", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_outreach_recipients_outreach_request_id", "outreach_recipients", ["outreach_request_id"])
    op.create_index("ix_outreach_recipients_expert_profile_id", "outreach_recipients", ["expert_profile_id"])

    op.create_table(
        "outreach_recipient_slots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("outreach_recipient_id", sa.String(), nullable=False),
        sa.Column("expert_availability_slot_id", sa.String(), nullable=False),
    )
    op.create_index("ix_outreach_recipient_slots_outreach_recipient_id", "outreach_recipient_slots", ["outreach_recipient_id"])
    op.create_index(
        "ix_outreach_recipient_slots_expert_availability_slot_id",
        "outreach_recipient_slots",
        ["expert_availability_slot_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_outreach_recipient_slots_expert_availability_slot_id", table_name="outreach_recipient_slots")
    op.drop_index("ix_outreach_recipient_slots_outreach_recipient_id", table_name="outreach_recipient_slots")
    op.drop_table("outreach_recipient_slots")
    op.drop_index("ix_outreach_recipients_expert_profile_id", table_name="outreach_recipients")
    op.drop_index("ix_outreach_recipients_outreach_request_id", table_name="outreach_recipients")
    op.drop_table("outreach_recipients")
    op.drop_index("ix_match_results_expert_search_document_id", table_name="match_results")
    op.drop_index("ix_match_results_expert_profile_id", table_name="match_results")
    op.drop_index("ix_match_results_expert_query_id", table_name="match_results")
    op.drop_table("match_results")
    op.drop_index("ix_requester_contacts_email", table_name="requester_contacts")
    op.drop_table("requester_contacts")
    op.drop_index("ix_expert_search_documents_source_record_id", table_name="expert_search_documents")
    op.drop_index("ix_expert_search_documents_expert_profile_id", table_name="expert_search_documents")
    op.drop_table("expert_search_documents")
    op.drop_index("ix_publication_records_external_work_id", table_name="publication_records")
    op.drop_index("ix_publication_records_expert_profile_id", table_name="publication_records")
    op.drop_table("publication_records")
    op.drop_index("ix_expert_enrichment_runs_expert_profile_id", table_name="expert_enrichment_runs")
    op.drop_table("expert_enrichment_runs")
    op.drop_index("ix_expert_edit_sessions_token_hash", table_name="expert_edit_sessions")
    op.drop_index("ix_expert_edit_sessions_expert_profile_id", table_name="expert_edit_sessions")
    op.drop_table("expert_edit_sessions")
    op.drop_index("ix_expertise_entries_expert_profile_id", table_name="expertise_entries")
    op.drop_table("expertise_entries")
    op.alter_column("expert_queries", "requester_contact_id", existing_type=sa.String(), nullable=False)
    op.drop_column("expert_profiles", "deleted_at")
