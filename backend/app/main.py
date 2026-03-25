from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import database_is_configured, ensure_pgvector_extension, get_engine, get_session_factory
from app.services.availability_service import AvailabilityService
from app.services.email_service import EmailService
from app.services.embedding_service import EmbeddingService
from app.services.expert_profile_service import ExpertProfileService
from app.services.matching_service import MatchingService
from app.services.openalex_client import OpenAlexClient
from app.services.orcid_client import OrcidClient
from app.services.outreach_service import OutreachService
from app.services.retrieval_service import RetrievalService


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    if not settings.postgres_dsn:
        raise RuntimeError("POSTGRES_DSN must be configured")
    app.state.settings = settings
    app.state.database_configured = database_is_configured(settings)
    ensure_pgvector_extension(get_engine(settings.postgres_dsn))
    session_factory = get_session_factory(settings)
    email_service = EmailService(settings=settings)
    embedding_service = EmbeddingService(settings=settings)
    retrieval_service = RetrievalService()
    orcid_client = OrcidClient(settings=settings)
    openalex_client = OpenAlexClient(settings=settings)
    availability_service = AvailabilityService(session_factory=session_factory)
    expert_profile_service = ExpertProfileService(
        session_factory=session_factory,
        settings=settings,
        embedding_service=embedding_service,
        availability_service=availability_service,
        orcid_client=orcid_client,
        openalex_client=openalex_client,
    )
    matching_service = MatchingService(
        session_factory=session_factory,
        settings=settings,
        embedding_service=embedding_service,
        retrieval_service=retrieval_service,
    )
    outreach_service = OutreachService(
        session_factory=session_factory,
        email_service=email_service,
        availability_service=availability_service,
    )
    app.state.services = {
        "availability": availability_service,
        "expert_profile": expert_profile_service,
        "matching": matching_service,
        "outreach": outreach_service,
    }
    yield


app = FastAPI(title="Expert Match API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)
