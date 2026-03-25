from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SlotSummary(APIModel):
    slot_id: UUID
    local_date: date
    local_start_time: time
    is_available: bool
    attendee_request_count: int
