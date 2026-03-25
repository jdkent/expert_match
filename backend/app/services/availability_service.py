from __future__ import annotations

from copy import deepcopy
from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.store import EVENT_TIMEZONE, SLOT_CATALOG, SLOT_ID_LOOKUP
from app.models.expert_availability_slot import ExpertAvailabilitySlot
from app.models.expert_profile import ExpertProfile


class AvailabilityService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def initialize_for_profile(
        self, profile_id: UUID | str, available_slot_ids: list[UUID] | None = None
    ) -> list[ExpertAvailabilitySlot]:
        allowed = {str(slot_id) for slot_id in available_slot_ids} if available_slot_ids is not None else None
        availability: list[ExpertAvailabilitySlot] = []
        for slot in SLOT_CATALOG:
            is_available = True if allowed is None else str(slot["slot_id"]) in allowed
            availability.append(
                ExpertAvailabilitySlot(
                    id=str(uuid4()),
                    expert_profile_id=str(profile_id),
                    canonical_slot_id=str(slot["slot_id"]),
                    slot_start_at=slot["slot_start"],
                    slot_end_at=slot["slot_end"],
                    timezone=EVENT_TIMEZONE,
                    local_date=slot["local_date"],
                    local_start_time=slot["local_start_time"],
                    is_available=is_available,
                    attendee_request_count=0,
                )
            )
        return availability

    def replace_for_profile(
        self,
        profile_id: UUID | str,
        available_slot_ids: list[UUID] | None,
        *,
        session: Session | None = None,
    ) -> None:
        own_session = session is None
        session = session or self.session_factory()
        try:
            existing_counts = {
                slot.canonical_slot_id: slot.attendee_request_count
                for slot in session.scalars(
                    select(ExpertAvailabilitySlot).where(
                        ExpertAvailabilitySlot.expert_profile_id == str(profile_id)
                    )
                ).all()
            }
            session.execute(
                delete(ExpertAvailabilitySlot).where(ExpertAvailabilitySlot.expert_profile_id == str(profile_id))
            )
            replacement_slots = self.initialize_for_profile(profile_id, available_slot_ids)
            for slot in replacement_slots:
                slot.attendee_request_count = existing_counts.get(slot.canonical_slot_id, 0)
            session.add_all(replacement_slots)
            if own_session:
                session.commit()
        except Exception:
            if own_session:
                session.rollback()
            raise
        finally:
            if own_session:
                session.close()

    def list_for_profile(self, profile_id: UUID | str) -> list[dict]:
        with self.session_factory() as session:
            profile_id_str = str(profile_id)
            profile = session.get(ExpertProfile, profile_id_str)
            if profile is None or profile.deleted_at is not None:
                raise HTTPException(status_code=404, detail="Expert not found")
            slots = session.scalars(
                select(ExpertAvailabilitySlot)
                .where(ExpertAvailabilitySlot.expert_profile_id == profile_id_str)
                .order_by(ExpertAvailabilitySlot.slot_start_at.asc())
            ).all()
            return [
                {
                    "slot_id": slot.canonical_slot_id,
                    "local_date": slot.local_date,
                    "local_start_time": slot.local_start_time,
                    "is_available": slot.is_available,
                    "attendee_request_count": slot.attendee_request_count,
                }
                for slot in slots
            ]

    def get_slot(
        self,
        profile_id: UUID | str,
        slot_id: UUID,
        *,
        session: Session | None = None,
    ) -> ExpertAvailabilitySlot:
        own_session = session is None
        session = session or self.session_factory()
        try:
            profile_id_str = str(profile_id)
            profile = session.get(ExpertProfile, profile_id_str)
            if profile is None or profile.deleted_at is not None:
                raise HTTPException(status_code=404, detail="Expert not found")
            slot = session.scalar(
                select(ExpertAvailabilitySlot).where(
                    ExpertAvailabilitySlot.expert_profile_id == profile_id_str,
                    ExpertAvailabilitySlot.canonical_slot_id == str(slot_id),
                )
            )
            if slot is None:
                if slot_id not in SLOT_ID_LOOKUP:
                    raise HTTPException(status_code=422, detail="Unknown slot id")
                raise HTTPException(status_code=404, detail="Slot not found for expert")
            return slot
        finally:
            if own_session:
                session.close()

    def increment_slot_counts(
        self,
        profile_id: UUID | str,
        slot_ids: list[UUID],
        *,
        session: Session | None = None,
    ) -> list[ExpertAvailabilitySlot]:
        own_session = session is None
        session = session or self.session_factory()
        updated_slots: list[ExpertAvailabilitySlot] = []
        try:
            for slot_id in slot_ids:
                slot = self.get_slot(profile_id, slot_id, session=session)
                if not slot.is_available:
                    raise HTTPException(status_code=422, detail="Selected slot is unavailable")
                slot.attendee_request_count += 1
                updated_slots.append(slot)
            if own_session:
                session.commit()
            return updated_slots
        except Exception:
            if own_session:
                session.rollback()
            raise
        finally:
            if own_session:
                session.close()

    def snapshot(self, profile_id: UUID | str) -> list[dict]:
        return deepcopy(self.list_for_profile(profile_id))
