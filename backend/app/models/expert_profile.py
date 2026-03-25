from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExpertProfile(Base):
    __tablename__ = "expert_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    short_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    orcid_id: Mapped[str | None] = mapped_column(String(19), unique=True, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    x_handle: Mapped[str | None] = mapped_column(String(128), nullable=True)
    linkedin_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bluesky_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    orcid_validation_status: Mapped[str] = mapped_column(String(32), default="not_provided")
    discoverability_status: Mapped[str] = mapped_column(String(64), default="pending_enrichment")
    access_key_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class ExpertiseEntry(Base):
    __tablename__ = "expertise_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    entry_text: Mapped[str] = mapped_column(Text)
    entry_order: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
class ExpertEnrichmentRun(Base):
    __tablename__ = "expert_enrichment_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    trigger_source: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    publication_selected_count: Mapped[int] = mapped_column(default=0)
    publication_embedded_count: Mapped[int] = mapped_column(default=0)
    availability_initialized: Mapped[bool] = mapped_column(default=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
