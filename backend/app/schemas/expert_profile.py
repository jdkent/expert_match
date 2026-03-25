from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.schemas.common import APIModel, SlotSummary


ExpertiseEntries = Annotated[list[str], Field(min_length=1)]


class ExpertProfileInput(BaseModel):
    full_name: str
    email: EmailStr
    short_bio: str | None = Field(default=None, max_length=500)
    orcid_id: str | None = None
    website_url: HttpUrl | None = None
    x_handle: str | None = None
    linkedin_identifier: str | None = None
    bluesky_identifier: str | None = None
    github_handle: str | None = None
    expertise_entries: ExpertiseEntries
    available_slot_ids: list[UUID] | None = None


class ExpertProfileEditInput(BaseModel):
    full_name: str | None = None
    short_bio: str | None = Field(default=None, max_length=500)
    orcid_id: str | None = None
    website_url: HttpUrl | None = None
    x_handle: str | None = None
    linkedin_identifier: str | None = None
    bluesky_identifier: str | None = None
    github_handle: str | None = None
    expertise_entries: ExpertiseEntries | None = None
    available_slot_ids: list[UUID] | None = None


class ExpertProfileAccessInput(BaseModel):
    access_key: str


class ExpertProfileAccepted(APIModel):
    profile_id: UUID
    access_key: str


class ExpertProfileAccessEditInput(ExpertProfileEditInput):
    access_key: str


class ExpertProfileDeleteInput(BaseModel):
    access_key: str
    email_confirmation: EmailStr


class ExpertProfileSummary(APIModel):
    expert_id: UUID
    full_name: str
    email: EmailStr
    short_bio: str | None = None
    orcid_id: str | None = None
    website_url: str | None = None
    x_handle: str | None = None
    linkedin_identifier: str | None = None
    bluesky_identifier: str | None = None
    github_handle: str | None = None
    expertise_entries: list[str]
    availability_slots: list[SlotSummary]
