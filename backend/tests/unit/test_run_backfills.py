from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy import select

from app.core.config import DEFAULT_SIMILARITY_THRESHOLD
from app.models.backfill_run import BackfillRun
from app.models.enums import DiscoverabilityStatus, SourceType
from app.models.expert_profile import ExpertProfile
from app.models.expert_query import ExpertQuery
from app.models.publication_record import ExpertSearchDocument
from app.scripts.run_backfills import (
    LABEL_BACKFILL_NAME,
    REEMBED_BACKFILL_NAME,
    mark_legacy_embeddings,
    reembed_search_documents,
)


def test_mark_legacy_embeddings_is_idempotent(session_factory):
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
        session.add(
            ExpertSearchDocument(
                id=str(uuid4()),
                expert_profile_id=profile.id,
                source_type=SourceType.MANUAL_EXPERTISE.value,
                source_record_id=str(uuid4()),
                document_text="legacy embedding",
                embedding_vector=[1.0] + [0.0] * 767,
                embedding_model="mystery-model",
                is_active=True,
            )
        )
        session.add(
            ExpertQuery(
                id=str(uuid4()),
                query_text="metadata",
                query_embedding_vector=[1.0] + [0.0] * 767,
                embedding_model="mystery-model",
                similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
                search_status="ready",
            )
        )
        session.commit()

    updated = mark_legacy_embeddings(
        session_factory=session_factory,
        target_embedding_model="sentence-transformers/all-mpnet-base-v2",
    )
    repeated = mark_legacy_embeddings(
        session_factory=session_factory,
        target_embedding_model="sentence-transformers/all-mpnet-base-v2",
    )

    with session_factory() as session:
        run = session.scalar(select(BackfillRun).where(BackfillRun.name == LABEL_BACKFILL_NAME))
        labels = session.scalars(select(ExpertSearchDocument.embedding_model)).all()
        query_labels = session.scalars(select(ExpertQuery.embedding_model)).all()

    assert updated == 2
    assert repeated == 0
    assert run is not None
    assert run.status == "completed"
    assert labels == ["allenai/specter2"]
    assert query_labels == ["allenai/specter2"]


def test_reembed_search_documents_refreshes_profiles_missing_short_bio_documents(session_factory):
    with session_factory() as session:
        profile = ExpertProfile(
            id=str(uuid4()),
            full_name="Ada Lovelace",
            email="ada@example.org",
            short_bio="Computational creativity researcher.",
            discoverability_status=DiscoverabilityStatus.ACTIVE.value,
            access_key_hash="dummy",
        )
        session.add(profile)
        session.flush()
        session.add(
            ExpertSearchDocument(
                id=str(uuid4()),
                expert_profile_id=profile.id,
                source_type=SourceType.MANUAL_EXPERTISE.value,
                source_record_id=str(uuid4()),
                document_text="Metadata workflows",
                embedding_vector=[1.0] + [0.0] * 767,
                embedding_model="sentence-transformers/all-mpnet-base-v2",
                is_active=True,
            )
        )
        session.commit()

    service = Mock()

    processed = reembed_search_documents(
        session_factory=session_factory,
        service=service,
        target_embedding_model="sentence-transformers/all-mpnet-base-v2",
    )

    with session_factory() as session:
        run = session.scalar(select(BackfillRun).where(BackfillRun.name == REEMBED_BACKFILL_NAME))

    assert processed == 1
    assert service.refresh_search_documents.call_count == 1
    assert run is not None
    assert run.status == "completed"
