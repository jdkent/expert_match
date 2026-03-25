from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from app.core.store import normalize_email
from app.models.enums import DeliveryStatus, OutreachStatus
from app.models.expert_profile import ExpertProfile
from app.models.expert_query import ExpertQuery
from app.models.outreach_request import OutreachRecipient, OutreachRecipientSlot, OutreachRequest
from app.models.requester_contact import RequesterContact
from app.schemas.outreach import OutreachRequestInput
from app.services.availability_service import AvailabilityService
from app.services.email_service import EmailService


class OutreachService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        email_service: EmailService,
        availability_service: AvailabilityService,
    ) -> None:
        self.session_factory = session_factory
        self.email_service = email_service
        self.availability_service = availability_service

    def create_outreach_request(self, payload: OutreachRequestInput) -> dict:
        if payload.primary_expert_id not in {recipient.expert_id for recipient in payload.recipients}:
            raise HTTPException(status_code=422, detail="Primary expert must be one of the recipients")
        with self.session_factory() as session:
            try:
                if session.get(ExpertQuery, str(payload.match_query_id)) is None:
                    raise HTTPException(status_code=404, detail="Match query not found")
                requester = RequesterContact(
                    id=str(uuid4()),
                    full_name=payload.requester.full_name,
                    email=normalize_email(str(payload.requester.email)),
                    organization=payload.requester.organization,
                )
                session.add(requester)
                session.flush()
                subject = f"Expert match request from {payload.requester.full_name}"
                outreach = OutreachRequest(
                    id=str(uuid4()),
                    expert_query_id=str(payload.match_query_id),
                    requester_contact_id=requester.id,
                    primary_expert_profile_id=str(payload.primary_expert_id),
                    message_subject=subject,
                    message_body=payload.message_body,
                    overall_status=OutreachStatus.SENT.value,
                )
                session.add(outreach)
                session.flush()

                for recipient in payload.recipients:
                    profile = session.get(ExpertProfile, str(recipient.expert_id))
                    if profile is None or profile.deleted_at is not None:
                        raise HTTPException(status_code=404, detail="Recipient expert not found")
                    slots = []
                    if recipient.availability_slot_ids:
                        slots = self.availability_service.increment_slot_counts(
                            recipient.expert_id,
                            list(recipient.availability_slot_ids),
                            session=session,
                        )
                    message_body = self._format_message(
                        requester_name=payload.requester.full_name,
                        requester_email=str(payload.requester.email),
                        expert_name=profile.full_name,
                        base_message=payload.message_body,
                        slots=slots,
                        is_primary=recipient.expert_id == payload.primary_expert_id,
                    )
                    delivery_reference = self.email_service.send_email(
                        to_email=profile.email,
                        subject=subject,
                        body=message_body,
                    )
                    recipient_row = OutreachRecipient(
                        id=str(uuid4()),
                        outreach_request_id=outreach.id,
                        expert_profile_id=str(recipient.expert_id),
                        delivery_status=DeliveryStatus.SENT.value,
                        delivery_reference=delivery_reference,
                    )
                    session.add(recipient_row)
                    session.flush()
                    for slot in slots:
                        session.add(
                            OutreachRecipientSlot(
                                id=str(uuid4()),
                                outreach_recipient_id=recipient_row.id,
                                expert_availability_slot_id=slot.id,
                            )
                        )
                session.commit()
                return {
                    "outreach_request_id": outreach.id,
                    "overall_status": outreach.overall_status,
                    "message_subject": outreach.message_subject,
                }
            except Exception:
                session.rollback()
                raise

    @staticmethod
    def _format_message(
        *,
        requester_name: str,
        requester_email: str,
        expert_name: str,
        base_message: str,
        slots: list[object],
        is_primary: bool,
    ) -> str:
        slot_lines = [
            f"- {slot.local_date.isoformat()} {slot.local_start_time.strftime('%H:%M')} Europe/Paris"
            for slot in slots
        ]
        timing_block = "\n".join(slot_lines) if slot_lines else "No specific times proposed."
        priority_note = "Preferred expert" if is_primary else "Additional expert"
        return (
            f"Hello {expert_name},\n\n"
            f"{requester_name} ({requester_email}) contacted you through Expert Match.\n"
            f"Recipient type: {priority_note}\n\n"
            f"Question:\n{base_message}\n\n"
            f"Requested times:\n{timing_block}\n"
        )
