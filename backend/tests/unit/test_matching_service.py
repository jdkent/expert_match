from unittest.mock import Mock

from app.core.config import Settings
from app.db.session import database_is_configured
from app.services.matching_service import MatchingService
from tests.helpers import create_expert


def test_matching_service_deduplicates_experts(client):
    create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows", "Reproducible research"],
    )
    payload = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "reproducible research metadata",
        },
    ).json()
    assert len(payload["matches"]) == 1


def test_database_configuration_detects_dsn():
    assert database_is_configured(Settings(POSTGRES_DSN="postgresql+psycopg://example")) is True
    assert database_is_configured(Settings(POSTGRES_DSN=None)) is False


def test_matching_service_can_disable_publication_abstract_search():
    retrieval_service = Mock()
    service = MatchingService(
        session_factory=Mock(),
        settings=Settings(
            POSTGRES_DSN="postgresql+psycopg://example",
            search_include_publication_abstracts=False,
        ),
        embedding_service=Mock(),
        retrieval_service=retrieval_service,
    )

    assert service._allowed_source_types() == ["manual_expertise"]
