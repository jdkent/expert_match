from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OutreachRequest(Base):
    __tablename__ = "outreach_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_query_id: Mapped[str] = mapped_column(String, index=True)
    requester_contact_id: Mapped[str] = mapped_column(String, index=True)
    primary_expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    message_subject: Mapped[str] = mapped_column(String(255))
    message_body: Mapped[str] = mapped_column(Text)
    overall_status: Mapped[str] = mapped_column(String(32), default="draft")


class OutreachRecipient(Base):
    __tablename__ = "outreach_recipients"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    outreach_request_id: Mapped[str] = mapped_column(String, index=True)
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    delivery_status: Mapped[str] = mapped_column(String(32), default="pending")
    delivery_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)


class OutreachRecipientSlot(Base):
    __tablename__ = "outreach_recipient_slots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    outreach_recipient_id: Mapped[str] = mapped_column(String, index=True)
    expert_availability_slot_id: Mapped[str] = mapped_column(String, index=True)
