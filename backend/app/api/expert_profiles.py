from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_service
from app.schemas.expert_profile import (
    ExpertProfileAccessEditInput,
    ExpertProfileAccessInput,
    ExpertProfileAccepted,
    ExpertProfileDeleteInput,
    ExpertProfileEditInput,
    ExpertProfileInput,
    ExpertProfileSummary,
)

router = APIRouter()


def expert_profile_service(request: Request):
    return get_service(request, "expert_profile")


@router.post("/experts", status_code=status.HTTP_202_ACCEPTED, response_model=ExpertProfileAccepted)
def create_expert_profile(
    payload: ExpertProfileInput,
    service=Depends(expert_profile_service),
):
    return service.create_profile(payload)


@router.post("/expert-access/profile", response_model=ExpertProfileSummary)
def get_expert_profile_by_access_key(
    payload: ExpertProfileAccessInput,
    service=Depends(expert_profile_service),
):
    return service.get_profile_for_access_key(payload.access_key)


@router.patch("/expert-access/profile", status_code=status.HTTP_202_ACCEPTED)
def update_expert_profile_by_access_key(
    payload: ExpertProfileAccessEditInput,
    service=Depends(expert_profile_service),
):
    update_payload = ExpertProfileEditInput.model_validate(payload.model_dump(exclude={"access_key"}))
    return service.update_profile(payload.access_key, update_payload)


@router.delete("/expert-access/profile", status_code=status.HTTP_202_ACCEPTED)
def delete_expert_profile_by_access_key(
    payload: ExpertProfileDeleteInput,
    service=Depends(expert_profile_service),
):
    return service.delete_profile(payload.access_key, str(payload.email_confirmation))
