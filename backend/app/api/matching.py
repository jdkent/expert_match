from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_service
from app.schemas.matching import MatchQueryInput, MatchQueryResponse

router = APIRouter()


def matching_service(request: Request):
    return get_service(request, "matching")


@router.post(
    "/match-queries",
    status_code=status.HTTP_201_CREATED,
    response_model=MatchQueryResponse,
)
def create_match_query(payload: MatchQueryInput, service=Depends(matching_service)):
    return service.create_match_query(payload)
