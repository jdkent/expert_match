from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_service
from app.schemas.outreach import OutreachRequestInput, OutreachRequestResponse

router = APIRouter()


def outreach_service(request: Request):
    return get_service(request, "outreach")


@router.post(
    "/outreach-requests",
    status_code=status.HTTP_201_CREATED,
    response_model=OutreachRequestResponse,
)
def create_outreach_request(
    payload: OutreachRequestInput,
    service=Depends(outreach_service),
):
    return service.create_outreach_request(payload)
