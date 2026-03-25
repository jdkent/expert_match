from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_service
from app.schemas.common import SlotSummary

router = APIRouter()


def availability_service(request: Request):
    return get_service(request, "availability")


@router.get("/experts/{expert_id}/availability", response_model=list[SlotSummary])
def get_expert_availability(expert_id: UUID, service=Depends(availability_service)):
    return service.list_for_profile(expert_id)
