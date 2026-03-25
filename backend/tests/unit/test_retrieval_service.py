from uuid import uuid4

from sqlalchemy import select

from app.core.config import DEFAULT_SIMILARITY_THRESHOLD
from app.models.enums import DiscoverabilityStatus, SourceType
from app.models.expert_profile import ExpertProfile
from app.models.publication_record import ExpertSearchDocument
from app.services.retrieval_service import RetrievalService


def _vector(first_value: float) -> list[float]:
    return [first_value] + [0.0] * 767


def test_rank_documents_can_exclude_publication_abstracts(session_factory):
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
        all_rows = retrieval_service.rank_documents(
            session=session,
            query_vector=_vector(1.0),
            similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
            allowed_source_types=[
                SourceType.MANUAL_EXPERTISE.value,
                SourceType.PUBLICATION_ABSTRACT.value,
            ],
        )
        manual_only_rows = retrieval_service.rank_documents(
            session=session,
            query_vector=_vector(1.0),
            similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
            allowed_source_types=[SourceType.MANUAL_EXPERTISE.value],
        )

    assert len(all_rows) == 2
    assert len(manual_only_rows) == 1
    assert manual_only_rows[0][1].source_type == SourceType.MANUAL_EXPERTISE.value
