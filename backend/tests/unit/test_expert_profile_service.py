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
            short_bio="Cognitive neuroscientist focused on reproducible neuroimaging methods.",
            orcid_id="0000-0001-6755-0259",
            expertise_entries=["Metadata workflows"],
        )
    )
    service.wait_for_idle(timeout=120)
    with session_factory() as session:
        profile = session.get(ExpertProfile, accepted["profile_id"])
        assert profile.discoverability_status == "active"
        assert profile.access_key_hash
        assert profile.short_bio == "Cognitive neuroscientist focused on reproducible neuroimaging methods."
        assert len(service.availability_service.list_for_profile(accepted["profile_id"])) == 180
        assert session.scalar(select(func.count()).select_from(PublicationRecord)) > 0
        assert session.scalar(select(func.count()).select_from(ExpertSearchDocument)) > 1


def test_access_key_unlocks_profile_updates(session_factory):
    settings = Settings(
        postgres_dsn=get_settings().postgres_dsn,
        openalex_enabled=True,
        orcid_live_validation=True,
        embedding_cache_dir=get_settings().embedding_cache_dir,
    )
    service = build_service(session_factory, settings=settings)
    accepted = service.create_profile(
        ExpertProfileInput(
            full_name="Ada Lovelace",
            email="ada@example.org",
            short_bio="Mathematician and computing pioneer.",
            expertise_entries=["Metadata workflows"],
        )
    )
    service.wait_for_idle(timeout=30)
    profile = service.get_profile_for_access_key(accepted["access_key"])
    assert profile["email"] == "ada@example.org"
    assert profile["short_bio"] == "Mathematician and computing pioneer."
    updated = service.update_profile(
        accepted["access_key"],
        ExpertProfileEditInput(
            short_bio="Mathematician focused on analytical engines.",
            expertise_entries=["Metadata workflows", "ORCID support"],
        ),
    )
    service.wait_for_idle(timeout=30)
    assert updated["status"] == "updated"
    refreshed_profile = service.get_profile_for_access_key(accepted["access_key"])
    assert refreshed_profile["short_bio"] == "Mathematician focused on analytical engines."


def test_refresh_search_documents_includes_short_bio(session_factory):
    settings = Settings(
        postgres_dsn=get_settings().postgres_dsn,
        openalex_enabled=False,
        orcid_live_validation=False,
        embedding_cache_dir=get_settings().embedding_cache_dir,
    )
    service = build_service(session_factory, settings=settings)
    accepted = service.create_profile(
        ExpertProfileInput(
            full_name="Grace Hopper",
            email="grace@example.org",
            short_bio="Compiler pioneer focused on programming language tooling.",
            expertise_entries=["Distributed systems"],
        )
    )
    service.wait_for_idle(timeout=30)

    with session_factory() as session:
        search_documents = session.scalars(
            select(ExpertSearchDocument)
            .where(ExpertSearchDocument.expert_profile_id == accepted["profile_id"])
            .order_by(ExpertSearchDocument.source_type.asc(), ExpertSearchDocument.document_text.asc())
        ).all()

    assert [document.source_type for document in search_documents] == ["manual_expertise", "short_bio"]
    assert [document.document_text for document in search_documents] == [
        "Distributed systems",
        "Compiler pioneer focused on programming language tooling.",
    ]
