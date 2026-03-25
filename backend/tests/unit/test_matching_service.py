from unittest.mock import MagicMock, Mock
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

    assert service._allowed_source_types() == ["manual_expertise", "short_bio"]


def test_matching_service_rejects_semantic_only_rank_one_match_at_default_threshold():
    session_factory = MagicMock()
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
    retrieval_service.rank_lexical_documents.return_value = []
    retrieval_service.rank_semantic_documents.return_value = [
        type("RankedDocument", (), {"profile": profile, "document": document, "score": 0.91})()
    ]

    service = MatchingService(
        session_factory=Mock(return_value=session),
        settings=Settings(POSTGRES_DSN="postgresql+psycopg://example"),
        embedding_service=embedding_service,
        retrieval_service=retrieval_service,
    )

    payload = service.create_match_query(type("Payload", (), {"query_text": "socks"})())

    assert payload["matches"] == []


def test_matching_service_fuses_lexical_and_semantic_rankings():
    session = MagicMock()
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

    top_profile = ExpertProfile(
        id=str(uuid4()),
        full_name="Ada Lovelace",
        email="ada@example.org",
        access_key_hash="dummy-top",
    )
    second_profile = ExpertProfile(
        id=str(uuid4()),
        full_name="Grace Hopper",
        email="grace@example.org",
        access_key_hash="dummy-second",
    )
    top_document = ExpertSearchDocument(
        id=str(uuid4()),
        expert_profile_id=top_profile.id,
        source_type="manual_expertise",
        source_record_id=str(uuid4()),
        document_text="metadata workflows for reproducible science",
        embedding_vector=[1.0] + [0.0] * 767,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        is_active=True,
    )
    second_document = ExpertSearchDocument(
        id=str(uuid4()),
        expert_profile_id=second_profile.id,
        source_type="manual_expertise",
        source_record_id=str(uuid4()),
        document_text="reproducible computing systems",
        embedding_vector=[1.0] + [0.0] * 767,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        is_active=True,
    )

    retrieval_service = Mock()
    retrieval_service.rank_lexical_documents.return_value = [
        type("RankedDocument", (), {"profile": top_profile, "document": top_document, "score": 7.5})(),
        type("RankedDocument", (), {"profile": second_profile, "document": second_document, "score": 6.0})(),
    ]
    retrieval_service.rank_semantic_documents.return_value = [
        type("RankedDocument", (), {"profile": second_profile, "document": second_document, "score": 0.92})(),
        type("RankedDocument", (), {"profile": top_profile, "document": top_document, "score": 0.91})(),
    ]

    service = MatchingService(
        session_factory=Mock(return_value=session),
        settings=Settings(POSTGRES_DSN="postgresql+psycopg://example"),
        embedding_service=embedding_service,
        retrieval_service=retrieval_service,
    )

    payload = service.create_match_query(type("Payload", (), {"query_text": "reproducible metadata workflows"})())

    assert [match["expert_id"] for match in payload["matches"]] == [second_profile.id, top_profile.id]
    assert payload["matches"][0]["aggregate_similarity_score"] == payload["matches"][1]["aggregate_similarity_score"]


def test_matching_service_can_return_no_matches_when_rrf_scores_stay_below_threshold():
    session = MagicMock()
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
        document_text="metadata workflows",
        embedding_vector=[1.0] + [0.0] * 767,
        embedding_model="sentence-transformers/all-mpnet-base-v2",
        is_active=True,
    )

    retrieval_service = Mock()
    retrieval_service.rank_lexical_documents.return_value = []
    retrieval_service.rank_semantic_documents.return_value = [
        type("RankedDocument", (), {"profile": profile, "document": document, "score": 0.81})()
    ]

    service = MatchingService(
        session_factory=Mock(return_value=session),
        settings=Settings(
            POSTGRES_DSN="postgresql+psycopg://example",
            match_acceptance_threshold=0.75,
        ),
        embedding_service=embedding_service,
        retrieval_service=retrieval_service,
    )

    payload = service.create_match_query(type("Payload", (), {"query_text": "metadata workflows"})())

    assert payload["matches"] == []


def test_matching_service_matches_short_bio_content(client):
    expert_id = create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows"],
        short_bio="Focuses on computational creativity for scientific discovery.",
    )["profile_id"]

    payload = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "computational creativity for scientific discovery",
        },
    ).json()

    assert payload["matches"][0]["expert_id"] == expert_id
    assert payload["matches"][0]["short_bio"] == "Focuses on computational creativity for scientific discovery."
