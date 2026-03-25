from unittest.mock import Mock
from uuid import uuid4

from app.core.config import Settings
from app.db.session import database_is_configured
from app.models.expert_profile import ExpertProfile
from app.models.publication_record import ExpertSearchDocument
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


def test_short_query_requires_lexical_overlap():
    service = MatchingService(
        session_factory=Mock(),
        settings=Settings(POSTGRES_DSN="postgresql+psycopg://example"),
        embedding_service=Mock(),
        retrieval_service=Mock(),
    )

    assert service._passes_short_query_lexical_floor(query_text="socks", document_text="github workflows") is False
    assert (
        service._passes_short_query_lexical_floor(
            query_text="meta-analysis",
            document_text="fmri analysis workflows",
        )
        is True
    )


def test_long_query_does_not_require_lexical_overlap():
    service = MatchingService(
        session_factory=Mock(),
        settings=Settings(POSTGRES_DSN="postgresql+psycopg://example"),
        embedding_service=Mock(),
        retrieval_service=Mock(),
    )

    assert (
        service._passes_short_query_lexical_floor(
            query_text="I need someone who understands neuroimaging evidence synthesis methods",
            document_text="coordinate based meta-analysis workflows",
        )
        is True
    )


def test_matching_service_filters_short_query_matches_without_lexical_overlap():
    session_factory = Mock()
    session = session_factory.return_value.__enter__.return_value
    session_factory.return_value = session
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=None)
    session.add = Mock()
    session.flush = Mock()
    session.execute = Mock()
    session.commit = Mock()
    session.rollback = Mock()

    embedding_service = Mock()
    embedding_service.embed_query.return_value = [1.0] + [0.0] * 767
    embedding_service.query_embedding_label.return_value = "sentence-transformers/all-mpnet-base-v2"

    profile = ExpertProfile(
        id=str(uuid4()),
        full_name="Ada Lovelace",
        email="ada@example.org",
        access_key_hash="dummy",
    )
    document = ExpertSearchDocument(
        id=str(uuid4()),
        expert_profile_id=profile.id,
        source_type="manual_expertise",
        source_record_id=str(uuid4()),
        document_text="github workflows",
        embedding_vector=[1.0] + [0.0] * 767,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        is_active=True,
    )

    retrieval_service = Mock()
    retrieval_service.rank_documents.return_value = [(profile, document, 0.91)]

    service = MatchingService(
        session_factory=Mock(return_value=session),
        settings=Settings(POSTGRES_DSN="postgresql+psycopg://example"),
        embedding_service=embedding_service,
        retrieval_service=retrieval_service,
    )

    payload = service.create_match_query(type("Payload", (), {"query_text": "socks"})())

    assert payload["matches"] == []
