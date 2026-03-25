from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import APIModel


class RequesterForOutreach(BaseModel):
    full_name: str
    email: EmailStr
    organization: str | None = None


class OutreachRecipientInput(BaseModel):
    expert_id: UUID
    availability_slot_ids: list[UUID] = Field(default_factory=list)


class OutreachRequestInput(BaseModel):
    match_query_id: UUID
    primary_expert_id: UUID
    requester: RequesterForOutreach
    recipients: list[OutreachRecipientInput] = Field(min_length=1, max_length=5)
    message_body: str


class OutreachRequestResponse(APIModel):
    outreach_request_id: UUID
    overall_status: str
    message_subject: str
