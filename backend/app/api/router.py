from fastapi import APIRouter

from app.api.availability import router as availability_router
from app.api.expert_profiles import router as expert_profiles_router
from app.api.health import router as health_router
from app.api.matching import router as matching_router
from app.api.outreach import router as outreach_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(expert_profiles_router, prefix="/api/v1")
api_router.include_router(availability_router, prefix="/api/v1")
api_router.include_router(matching_router, prefix="/api/v1")
api_router.include_router(outreach_router, prefix="/api/v1")
