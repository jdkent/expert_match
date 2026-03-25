from __future__ import annotations

import argparse

from sqlalchemy import distinct, select, update

from app.core.config import LEGACY_EMBEDDING_MODEL_NAME, get_settings
from app.core.store import utcnow
from app.db.session import get_session_factory
from app.models.backfill_run import BackfillRun
from app.models.enums import EnrichmentTriggerSource
from app.models.expert_availability_slot import ExpertAvailabilitySlot
from app.models.expert_profile import ExpertProfile
from app.models.expert_query import ExpertQuery
from app.models.publication_record import ExpertSearchDocument
from app.services.availability_service import AvailabilityService
from app.services.embedding_service import EmbeddingService
from app.services.expert_profile_service import ExpertProfileService
from app.services.openalex_client import OpenAlexClient
from app.services.orcid_client import OrcidClient


LABEL_BACKFILL_NAME = "label_legacy_embedding_model_v1"
REEMBED_BACKFILL_NAME = "reembed_search_documents_v1"


def _completed_run(session, *, name: str, target_embedding_model: str) -> BackfillRun | None:
    return session.scalar(
        select(BackfillRun).where(
            BackfillRun.name == name,
            BackfillRun.target_embedding_model == target_embedding_model,
            BackfillRun.status == "completed",
        )
    )


def _upsert_run(session, *, name: str, target_embedding_model: str, status: str, details: str | None) -> BackfillRun:
    run = session.scalar(
        select(BackfillRun).where(
            BackfillRun.name == name,
            BackfillRun.target_embedding_model == target_embedding_model,
        )
    )
    if run is None:
        run = BackfillRun(
            name=name,
            target_embedding_model=target_embedding_model,
            status=status,
            details=details,
            completed_at=utcnow() if status == "completed" else None,
        )
        session.add(run)
        session.flush()
        return run
    run.status = status
    run.details = details
    if status == "completed":
        run.completed_at = utcnow()
    return run


def mark_legacy_embeddings(*, session_factory, target_embedding_model: str) -> int:
    with session_factory() as session:
        if _completed_run(
            session,
            name=LABEL_BACKFILL_NAME,
            target_embedding_model=target_embedding_model,
        ) is not None:
            return 0
        _upsert_run(
            session,
            name=LABEL_BACKFILL_NAME,
            target_embedding_model=target_embedding_model,
            status="running",
            details=f"Relabeling non-{target_embedding_model} rows to {LEGACY_EMBEDDING_MODEL_NAME}",
        )
        docs_updated = session.execute(
            update(ExpertSearchDocument)
            .where(ExpertSearchDocument.embedding_model != target_embedding_model)
            .values(embedding_model=LEGACY_EMBEDDING_MODEL_NAME)
        ).rowcount or 0
        queries_updated = session.execute(
            update(ExpertQuery)
            .where(ExpertQuery.embedding_model != target_embedding_model)
            .values(embedding_model=LEGACY_EMBEDDING_MODEL_NAME)
        ).rowcount or 0
        _upsert_run(
            session,
            name=LABEL_BACKFILL_NAME,
            target_embedding_model=target_embedding_model,
            status="completed",
            details=f"Relabeled {docs_updated} search documents and {queries_updated} expert queries",
        )
        session.commit()
        return docs_updated + queries_updated


def _profile_needs_reembedding(session, *, profile_id: str, target_embedding_model: str) -> bool:
    embedding_models = session.scalars(
        select(distinct(ExpertSearchDocument.embedding_model)).where(
            ExpertSearchDocument.expert_profile_id == profile_id,
            ExpertSearchDocument.is_active.is_(True),
        )
    ).all()
    return embedding_models != [target_embedding_model]


def reembed_search_documents(*, session_factory, service: ExpertProfileService, target_embedding_model: str) -> int:
    with session_factory() as session:
        if _completed_run(
            session,
            name=REEMBED_BACKFILL_NAME,
            target_embedding_model=target_embedding_model,
        ) is not None:
            return 0
        _upsert_run(
            session,
            name=REEMBED_BACKFILL_NAME,
            target_embedding_model=target_embedding_model,
            status="running",
            details="Refreshing expert search documents with the target embedding model",
        )
        profile_ids = session.scalars(
            select(ExpertProfile.id).where(ExpertProfile.deleted_at.is_(None))
        ).all()
        session.commit()

    processed = 0
    for profile_id in profile_ids:
        with session_factory() as session:
            profile = session.get(ExpertProfile, profile_id)
            if profile is None or profile.deleted_at is not None:
                continue
            if not _profile_needs_reembedding(
                session,
                profile_id=profile.id,
                target_embedding_model=target_embedding_model,
            ):
                continue
            selected_slot_ids = session.scalars(
                select(ExpertAvailabilitySlot.canonical_slot_id).where(
                    ExpertAvailabilitySlot.expert_profile_id == profile.id,
                    ExpertAvailabilitySlot.is_available.is_(True),
                )
            ).all()
            service.refresh_search_documents(
                session,
                profile=profile,
                trigger_source=EnrichmentTriggerSource.EXPERT_EDIT.value,
                available_slot_ids=selected_slot_ids,
            )
            profile.updated_at = utcnow()
            session.commit()
            processed += 1

    with session_factory() as session:
        _upsert_run(
            session,
            name=REEMBED_BACKFILL_NAME,
            target_embedding_model=target_embedding_model,
            status="completed",
            details=f"Re-embedded {processed} expert profiles",
        )
        session.commit()
    return processed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run idempotent database backfills.")
    parser.parse_args()

    settings = get_settings()
    session_factory = get_session_factory(settings)
    embedding_service = EmbeddingService(settings=settings)
    availability_service = AvailabilityService(session_factory=session_factory)
    orcid_client = OrcidClient(settings=settings)
    openalex_client = OpenAlexClient(settings=settings)
    service = ExpertProfileService(
        session_factory=session_factory,
        settings=settings,
        embedding_service=embedding_service,
        availability_service=availability_service,
        orcid_client=orcid_client,
        openalex_client=openalex_client,
    )
    try:
        relabeled = mark_legacy_embeddings(
            session_factory=session_factory,
            target_embedding_model=embedding_service.document_embedding_label(),
        )
        processed = reembed_search_documents(
            session_factory=session_factory,
            service=service,
            target_embedding_model=embedding_service.document_embedding_label(),
        )
    finally:
        service.shutdown()

    print(
        "completed backfills",
        f"relabeled_rows={relabeled}",
        f"reembedded_profiles={processed}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
