import pytest
from sqlalchemy import func, select

from app.core.config import Settings, get_settings
from app.models.expert_profile import ExpertProfile
from app.models.publication_record import ExpertSearchDocument, PublicationRecord
from app.services.availability_service import AvailabilityService
from app.services.embedding_service import EmbeddingService
from app.services.expert_profile_service import ExpertProfileService
from app.services.openalex_client import OpenAlexClient
from app.services.orcid_client import OrcidClient
from app.schemas.expert_profile import ExpertProfileEditInput, ExpertProfileInput


def build_service(session_factory, settings: Settings | None = None):
    settings = settings or Settings(
        postgres_dsn=get_settings().postgres_dsn,
        embedding_provider="specter2",
        openalex_enabled=True,
        orcid_live_validation=True,
        embedding_cache_dir=get_settings().embedding_cache_dir,
    )
    return ExpertProfileService(
        session_factory=session_factory,
        settings=settings,
        embedding_service=EmbeddingService(settings=settings),
        availability_service=AvailabilityService(session_factory=session_factory),
        orcid_client=OrcidClient(settings=settings),
        openalex_client=OpenAlexClient(settings=settings),
    )


@pytest.mark.vcr
def test_profile_creation_creates_slots_and_search_documents(session_factory):
    service = build_service(session_factory)
    accepted = service.create_profile(
        ExpertProfileInput(
            full_name="Russell Poldrack",
            email="russell@example.org",
            orcid_id="0000-0001-6755-0259",
            expertise_entries=["Metadata workflows"],
        )
    )
    service.wait_for_idle(timeout=120)
    with session_factory() as session:
        profile = session.get(ExpertProfile, accepted["profile_id"])
        assert profile.discoverability_status == "active"
        assert profile.access_key_hash
        assert len(service.availability_service.list_for_profile(accepted["profile_id"])) == 180
        assert session.scalar(select(func.count()).select_from(PublicationRecord)) > 0
        assert session.scalar(select(func.count()).select_from(ExpertSearchDocument)) > 1


def test_access_key_unlocks_profile_updates(session_factory):
    settings = Settings(
        postgres_dsn=get_settings().postgres_dsn,
        embedding_provider="specter2",
        openalex_enabled=True,
        orcid_live_validation=True,
        embedding_cache_dir=get_settings().embedding_cache_dir,
    )
    service = build_service(session_factory, settings=settings)
    accepted = service.create_profile(
        ExpertProfileInput(
            full_name="Ada Lovelace",
            email="ada@example.org",
            expertise_entries=["Metadata workflows"],
        )
    )
    service.wait_for_idle(timeout=30)
    profile = service.get_profile_for_access_key(accepted["access_key"])
    assert profile["email"] == "ada@example.org"
    updated = service.update_profile(
        accepted["access_key"],
        ExpertProfileEditInput(expertise_entries=["Metadata workflows", "ORCID support"]),
    )
    service.wait_for_idle(timeout=30)
    assert updated["status"] == "updated"
