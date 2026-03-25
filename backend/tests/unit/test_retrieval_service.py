from uuid import uuid4

from app.models.enums import DiscoverabilityStatus, SourceType
from app.models.expert_profile import ExpertProfile
from app.models.publication_record import ExpertSearchDocument
from app.services.retrieval_service import RetrievalService


def _vector(first_value: float) -> list[float]:
    return [first_value] + [0.0] * 767


def test_rank_semantic_documents_can_exclude_publication_abstracts(session_factory):
    retrieval_service = RetrievalService()
    with session_factory() as session:
        profile = ExpertProfile(
            id=str(uuid4()),
            full_name="Ada Lovelace",
            email="ada@example.org",
            discoverability_status=DiscoverabilityStatus.ACTIVE.value,
            access_key_hash="dummy",
        )
        session.add(profile)
        session.flush()
        session.add_all(
            [
                ExpertSearchDocument(
                    id=str(uuid4()),
                    expert_profile_id=profile.id,
                    source_type=SourceType.MANUAL_EXPERTISE.value,
                    source_record_id=str(uuid4()),
                    document_text="manual expertise",
                    embedding_vector=_vector(1.0),
                    embedding_model="test-model",
                    is_active=True,
                ),
                ExpertSearchDocument(
                    id=str(uuid4()),
                    expert_profile_id=profile.id,
                    source_type=SourceType.PUBLICATION_ABSTRACT.value,
                    source_record_id=str(uuid4()),
                    document_text="publication abstract",
                    embedding_vector=_vector(1.0),
                    embedding_model="test-model",
                    is_active=True,
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        all_rows = retrieval_service.rank_semantic_documents(
            session=session,
            query_vector=_vector(1.0),
            allowed_source_types=[
                SourceType.MANUAL_EXPERTISE.value,
                SourceType.PUBLICATION_ABSTRACT.value,
            ],
            embedding_model="test-model",
            limit=10,
        )
        manual_only_rows = retrieval_service.rank_semantic_documents(
            session=session,
            query_vector=_vector(1.0),
            allowed_source_types=[SourceType.MANUAL_EXPERTISE.value],
            embedding_model="test-model",
            limit=10,
        )

    assert len(all_rows) == 2
    assert len(manual_only_rows) == 1
    assert manual_only_rows[0].document.source_type == SourceType.MANUAL_EXPERTISE.value


def test_rank_semantic_documents_filters_to_requested_embedding_model(session_factory):
    retrieval_service = RetrievalService()
    with session_factory() as session:
        profile = ExpertProfile(
            id=str(uuid4()),
            full_name="Grace Hopper",
            email="grace@example.org",
            discoverability_status=DiscoverabilityStatus.ACTIVE.value,
            access_key_hash="dummy",
        )
        session.add(profile)
        session.flush()
        session.add_all(
            [
                ExpertSearchDocument(
                    id=str(uuid4()),
                    expert_profile_id=profile.id,
                    source_type=SourceType.MANUAL_EXPERTISE.value,
                    source_record_id=str(uuid4()),
                    document_text="legacy embedding",
                    embedding_vector=_vector(1.0),
                    embedding_model="allenai/specter2",
                    is_active=True,
                ),
                ExpertSearchDocument(
                    id=str(uuid4()),
                    expert_profile_id=profile.id,
                    source_type=SourceType.MANUAL_EXPERTISE.value,
                    source_record_id=str(uuid4()),
                    document_text="target embedding",
                    embedding_vector=_vector(1.0),
                    embedding_model="sentence-transformers/all-mpnet-base-v2",
                    is_active=True,
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        rows = retrieval_service.rank_semantic_documents(
            session=session,
            query_vector=_vector(1.0),
            allowed_source_types=[SourceType.MANUAL_EXPERTISE.value],
            embedding_model="sentence-transformers/all-mpnet-base-v2",
            limit=10,
        )

    assert len(rows) == 1
    assert rows[0].document.document_text == "target embedding"


def test_rank_lexical_documents_ranks_full_text_matches_first(session_factory):
    retrieval_service = RetrievalService()
    with session_factory() as session:
        first_profile = ExpertProfile(
            id=str(uuid4()),
            full_name="Ada Lovelace",
            email="ada@example.org",
            discoverability_status=DiscoverabilityStatus.ACTIVE.value,
            access_key_hash="dummy-ada",
        )
        second_profile = ExpertProfile(
            id=str(uuid4()),
            full_name="Grace Hopper",
            email="grace@example.org",
            discoverability_status=DiscoverabilityStatus.ACTIVE.value,
            access_key_hash="dummy-grace",
        )
        session.add_all([first_profile, second_profile])
        session.flush()
        session.add_all(
            [
                ExpertSearchDocument(
                    id=str(uuid4()),
                    expert_profile_id=first_profile.id,
                    source_type=SourceType.MANUAL_EXPERTISE.value,
                    source_record_id=str(uuid4()),
                    document_text="reproducible research metadata workflows",
                    embedding_vector=_vector(1.0),
                    embedding_model="test-model",
                    is_active=True,
                ),
                ExpertSearchDocument(
                    id=str(uuid4()),
                    expert_profile_id=second_profile.id,
                    source_type=SourceType.MANUAL_EXPERTISE.value,
                    source_record_id=str(uuid4()),
                    document_text="metadata catalogs for archival systems",
                    embedding_vector=_vector(1.0),
                    embedding_model="test-model",
                    is_active=True,
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        rows = retrieval_service.rank_lexical_documents(
            session=session,
            query_text="reproducible metadata workflows",
            allowed_source_types=[SourceType.MANUAL_EXPERTISE.value],
            limit=10,
        )

    assert len(rows) == 2
    assert rows[0].profile.full_name == "Ada Lovelace"
    assert rows[1].profile.full_name == "Grace Hopper"
    assert rows[0].score > rows[1].score
    assert rows[0].lexical_coverage == 1.0
    assert rows[1].lexical_coverage < rows[0].lexical_coverage
    assert rows[0].score > 0


def test_rank_lexical_documents_can_match_partial_overlap_query_terms(session_factory):
    retrieval_service = RetrievalService()
    with session_factory() as session:
        profile = ExpertProfile(
            id=str(uuid4()),
            full_name="BIDS Expert",
            email="bids@example.org",
            discoverability_status=DiscoverabilityStatus.ACTIVE.value,
            access_key_hash="dummy-bids",
        )
        session.add(profile)
        session.flush()
        session.add(
            ExpertSearchDocument(
                id=str(uuid4()),
                expert_profile_id=profile.id,
                source_type=SourceType.MANUAL_EXPERTISE.value,
                source_record_id=str(uuid4()),
                document_text="BIDS",
                embedding_vector=_vector(1.0),
                embedding_model="test-model",
                is_active=True,
            )
        )
        session.commit()

    with session_factory() as session:
        rows = retrieval_service.rank_lexical_documents(
            session=session,
            query_text="How do I organize my data into BIDS?",
            allowed_source_types=[SourceType.MANUAL_EXPERTISE.value],
            limit=10,
        )

    assert len(rows) == 1
    assert rows[0].profile.full_name == "BIDS Expert"
    assert 0 < rows[0].lexical_coverage < 1
    assert rows[0].score > 0
