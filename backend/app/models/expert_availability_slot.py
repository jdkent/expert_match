from __future__ import annotations

from datetime import date, datetime, time
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ExpertAvailabilitySlot(Base):
    __tablename__ = "expert_availability_slots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    canonical_slot_id: Mapped[str] = mapped_column(String, index=True)
    slot_start_at: Mapped[datetime] = mapped_column(DateTime)
    slot_end_at: Mapped[datetime] = mapped_column(DateTime)
    timezone: Mapped[str] = mapped_column(String(64), default="Europe/Paris")
    local_date: Mapped[date] = mapped_column(Date)
    local_start_time: Mapped[time] = mapped_column(Time)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    attendee_request_count: Mapped[int] = mapped_column(Integer, default=0)
