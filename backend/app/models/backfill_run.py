from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BackfillRun(Base):
    __tablename__ = "backfill_runs"
    __table_args__ = (UniqueConstraint("name", "target_embedding_model", name="uq_backfill_runs_name_model"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), index=True)
    target_embedding_model: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
