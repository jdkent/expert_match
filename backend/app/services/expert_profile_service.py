from __future__ import annotations

import secrets
from concurrent.futures import Future, ThreadPoolExecutor, wait
from threading import Lock
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.store import hash_token, normalize_email, utcnow
from app.models.enums import (
    DiscoverabilityStatus,
    EnrichmentStatus,
    EnrichmentTriggerSource,
    OrcidValidationStatus,
    SourceType,
)
from app.models.expert_availability_slot import ExpertAvailabilitySlot
from app.models.expert_profile import ExpertEnrichmentRun, ExpertProfile, ExpertiseEntry
from app.models.publication_record import ExpertSearchDocument, PublicationRecord
from app.schemas.expert_profile import ExpertProfileEditInput, ExpertProfileInput
from app.services.availability_service import AvailabilityService
from app.services.embedding_service import EmbeddingService
from app.services.openalex_client import OpenAlexClient
from app.services.orcid_client import OrcidClient


class ExpertProfileService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        settings: Settings,
        embedding_service: EmbeddingService,
        availability_service: AvailabilityService,
        orcid_client: OrcidClient,
        openalex_client: OpenAlexClient,
        enrichment_executor: ThreadPoolExecutor | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings
        self.embedding_service = embedding_service
        self.availability_service = availability_service
        self.orcid_client = orcid_client
        self.openalex_client = openalex_client
        self.enrichment_executor = enrichment_executor or ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="expert-enrichment",
        )
        self._executor_owned = enrichment_executor is None
        self._enrichment_futures: set[Future[None]] = set()
        self._futures_lock = Lock()

    def create_profile(self, payload: ExpertProfileInput) -> dict:
        normalized_email = normalize_email(str(payload.email))
        self._validate_orcid(payload.orcid_id)
        access_key = self._new_token()
        selected_slot_ids = (
            [str(slot_id) for slot_id in payload.available_slot_ids]
            if payload.available_slot_ids is not None
            else None
        )
        with self.session_factory() as session:
            try:
                profile = session.scalar(
                    select(ExpertProfile).where(ExpertProfile.email == normalized_email)
                )
                if profile is None:
                    profile = ExpertProfile(
                        id=str(uuid4()),
                        full_name=payload.full_name.strip(),
                        email=normalized_email,
                        orcid_id=payload.orcid_id,
                        website_url=str(payload.website_url) if payload.website_url else None,
                        x_handle=payload.x_handle,
                        linkedin_identifier=payload.linkedin_identifier,
                        bluesky_identifier=payload.bluesky_identifier,
                        github_handle=payload.github_handle,
                        orcid_validation_status=self._orcid_status(payload.orcid_id),
                        discoverability_status=DiscoverabilityStatus.PENDING_ENRICHMENT.value,
                        access_key_hash=hash_token(access_key),
                        deleted_at=None,
                        created_at=utcnow(),
                        updated_at=utcnow(),
                    )
                    session.add(profile)
                    session.flush()
                else:
                    if profile.deleted_at is None:
                        raise HTTPException(
                            status_code=409,
                            detail="A profile already exists for this email address; use the expert access key to update it.",
                        )
                    profile.full_name = payload.full_name.strip()
                    profile.orcid_id = payload.orcid_id
                    profile.website_url = str(payload.website_url) if payload.website_url else None
                    profile.x_handle = payload.x_handle
                    profile.linkedin_identifier = payload.linkedin_identifier
                    profile.bluesky_identifier = payload.bluesky_identifier
                    profile.github_handle = payload.github_handle
                    profile.orcid_validation_status = self._orcid_status(payload.orcid_id)
                    profile.discoverability_status = DiscoverabilityStatus.PENDING_ENRICHMENT.value
                    profile.access_key_hash = hash_token(access_key)
                    profile.deleted_at = None
                    profile.updated_at = utcnow()
                self._replace_expertise_entries(session, profile.id, payload.expertise_entries)
                self.availability_service.replace_for_profile(profile.id, selected_slot_ids, session=session)
                profile.updated_at = utcnow()
                profile_id = profile.id
                session.commit()
            except Exception:
                session.rollback()
                raise
        self.enqueue_search_refresh(
            profile_id=profile_id,
            trigger_source=EnrichmentTriggerSource.INITIAL_SUBMISSION.value,
            available_slot_ids=selected_slot_ids,
            activate_on_completion=True,
        )
        return {"profile_id": profile_id, "access_key": access_key}

    def get_profile_for_access_key(self, access_key: str) -> dict:
        with self.session_factory() as session:
            profile = self._profile_for_access_key(session, access_key)
            return self._serialize_profile(session, profile)

    def update_profile(self, access_key: str, payload: ExpertProfileEditInput) -> dict:
        with self.session_factory() as session:
            try:
                profile = self._profile_for_access_key(session, access_key)
                if payload.full_name is not None:
                    profile.full_name = payload.full_name.strip()
                if "orcid_id" in payload.model_fields_set:
                    self._validate_orcid(payload.orcid_id)
                    profile.orcid_id = payload.orcid_id
                    profile.orcid_validation_status = self._orcid_status(payload.orcid_id)
                for field_name in (
                    "website_url",
                    "x_handle",
                    "linkedin_identifier",
                    "bluesky_identifier",
                    "github_handle",
                ):
                    if field_name in payload.model_fields_set:
                        value = getattr(payload, field_name)
                        setattr(profile, field_name, str(value) if value is not None else None)
                if payload.expertise_entries is not None:
                    if len(payload.expertise_entries) == 0:
                        raise HTTPException(status_code=422, detail="At least one expertise entry is required")
                    self._replace_expertise_entries(session, profile.id, payload.expertise_entries)
                selected_slot_ids = (
                    payload.available_slot_ids
                    if "available_slot_ids" in payload.model_fields_set
                    else self._selected_slot_ids(session, profile.id)
                )
                self.availability_service.replace_for_profile(
                    profile.id,
                    selected_slot_ids if selected_slot_ids else None,
                    session=session,
                )
                profile.updated_at = utcnow()
                profile_id = profile.id
                session.commit()
            except Exception:
                session.rollback()
                raise
        self.enqueue_search_refresh(
            profile_id=profile_id,
            trigger_source=EnrichmentTriggerSource.EXPERT_EDIT.value,
            available_slot_ids=selected_slot_ids if selected_slot_ids else None,
            activate_on_completion=False,
        )
        return {"profile_id": profile_id, "status": "updated"}

    def delete_profile(self, access_key: str, email_confirmation: str) -> dict:
        with self.session_factory() as session:
            try:
                profile = self._profile_for_access_key(session, access_key)
                if normalize_email(email_confirmation) != profile.email:
                    raise HTTPException(status_code=422, detail="Email confirmation does not match")
                profile.deleted_at = utcnow()
                profile.discoverability_status = DiscoverabilityStatus.ARCHIVED.value
                profile.access_key_hash = None
                profile.updated_at = utcnow()
                session.execute(delete(ExpertiseEntry).where(ExpertiseEntry.expert_profile_id == profile.id))
                session.execute(
                    delete(ExpertAvailabilitySlot).where(ExpertAvailabilitySlot.expert_profile_id == profile.id)
                )
                session.execute(delete(PublicationRecord).where(PublicationRecord.expert_profile_id == profile.id))
                session.execute(
                    delete(ExpertSearchDocument).where(ExpertSearchDocument.expert_profile_id == profile.id)
                )
                session.commit()
                return {"profile_id": profile.id, "status": "deleted"}
            except Exception:
                session.rollback()
                raise

    def refresh_search_documents(
        self,
        session: Session,
        *,
        profile: ExpertProfile,
        trigger_source: str,
        available_slot_ids: list[str | object] | None,
    ) -> None:
        run = ExpertEnrichmentRun(
            id=str(uuid4()),
            expert_profile_id=profile.id,
            trigger_source=trigger_source,
            status=EnrichmentStatus.RUNNING.value,
            publication_selected_count=0,
            publication_embedded_count=0,
            availability_initialized=False,
            last_error=None,
        )
        session.add(run)
        try:
            session.execute(delete(ExpertSearchDocument).where(ExpertSearchDocument.expert_profile_id == profile.id))
            session.execute(delete(PublicationRecord).where(PublicationRecord.expert_profile_id == profile.id))
            expertise_entries = session.scalars(
                select(ExpertiseEntry)
                .where(ExpertiseEntry.expert_profile_id == profile.id, ExpertiseEntry.is_active.is_(True))
                .order_by(ExpertiseEntry.entry_order.asc())
            ).all()
            for expertise in expertise_entries:
                vector = self.embedding_service.embed_document(expertise.entry_text)
                session.add(
                    ExpertSearchDocument(
                        id=str(uuid4()),
                        expert_profile_id=profile.id,
                        source_type=SourceType.MANUAL_EXPERTISE.value,
                        source_record_id=expertise.id,
                        document_text=expertise.entry_text,
                        embedding_vector=vector,
                        embedding_model=self.embedding_service.document_embedding_label(),
                        is_active=True,
                    )
                )
            publications = []
            if profile.orcid_id:
                publications = self.openalex_client.lookup_recent_publications(profile.orcid_id, max_results=25)
            for publication in publications:
                publication_record = PublicationRecord(
                    id=str(uuid4()),
                    expert_profile_id=profile.id,
                    external_work_id=publication["external_work_id"],
                    title=publication["title"],
                    publication_date=publication["publication_date"],
                    author_position=publication["author_position"],
                    author_priority=publication["author_priority"],
                    abstract_text=publication["abstract_text"],
                    abstract_status=publication["abstract_status"],
                    selected_for_enrichment=True,
                    is_active=True,
                )
                session.add(publication_record)
                session.flush()
                if publication_record.abstract_text:
                    vector = self.embedding_service.embed_document(publication_record.abstract_text)
                    session.add(
                        ExpertSearchDocument(
                            id=str(uuid4()),
                            expert_profile_id=profile.id,
                            source_type=SourceType.PUBLICATION_ABSTRACT.value,
                            source_record_id=publication_record.id,
                            document_text=publication_record.abstract_text,
                            embedding_vector=vector,
                            embedding_model=self.embedding_service.document_embedding_label(),
                            is_active=True,
                        )
                    )
            normalized_slot_ids = [str(slot_id) for slot_id in available_slot_ids] if available_slot_ids else None
            self.availability_service.replace_for_profile(profile.id, normalized_slot_ids, session=session)
            run.publication_selected_count = len(publications)
            run.publication_embedded_count = sum(1 for publication in publications if publication["abstract_text"])
            run.availability_initialized = True
            run.status = EnrichmentStatus.COMPLETED.value
        except Exception as exc:
            run.status = EnrichmentStatus.FAILED.value
            run.last_error = str(exc)
            raise

    def enqueue_search_refresh(
        self,
        *,
        profile_id: str,
        trigger_source: str,
        available_slot_ids: list[str | object] | None,
        activate_on_completion: bool,
    ) -> None:
        future = self.enrichment_executor.submit(
            self._run_search_refresh,
            profile_id=profile_id,
            trigger_source=trigger_source,
            available_slot_ids=available_slot_ids,
            activate_on_completion=activate_on_completion,
        )
        with self._futures_lock:
            self._enrichment_futures.add(future)
        future.add_done_callback(self._cleanup_enrichment_future)

    def wait_for_idle(self, timeout: float | None = None) -> None:
        with self._futures_lock:
            futures = list(self._enrichment_futures)
        if not futures:
            return
        _, not_done = wait(futures, timeout=timeout)
        if not_done:
            raise TimeoutError("Timed out waiting for expert enrichment to finish")

    def shutdown(self) -> None:
        if self._executor_owned:
            self.enrichment_executor.shutdown(wait=True, cancel_futures=False)

    def _run_search_refresh(
        self,
        *,
        profile_id: str,
        trigger_source: str,
        available_slot_ids: list[str | object] | None,
        activate_on_completion: bool,
    ) -> None:
        with self.session_factory() as session:
            try:
                profile = session.get(ExpertProfile, profile_id)
                if profile is None or profile.deleted_at is not None:
                    return
                self.refresh_search_documents(
                    session,
                    profile=profile,
                    trigger_source=trigger_source,
                    available_slot_ids=available_slot_ids,
                )
                if activate_on_completion:
                    profile.discoverability_status = DiscoverabilityStatus.ACTIVE.value
                profile.updated_at = utcnow()
                session.commit()
            except Exception:
                session.rollback()
                raise

    def _cleanup_enrichment_future(self, future: Future[None]) -> None:
        with self._futures_lock:
            self._enrichment_futures.discard(future)

    def _serialize_profile(self, session: Session, profile: ExpertProfile) -> dict:
        expertise_entries = session.scalars(
            select(ExpertiseEntry)
            .where(ExpertiseEntry.expert_profile_id == profile.id, ExpertiseEntry.is_active.is_(True))
            .order_by(ExpertiseEntry.entry_order.asc())
        ).all()
        return {
            "expert_id": profile.id,
            "full_name": profile.full_name,
            "email": profile.email,
            "orcid_id": profile.orcid_id,
            "website_url": profile.website_url,
            "x_handle": profile.x_handle,
            "linkedin_identifier": profile.linkedin_identifier,
            "bluesky_identifier": profile.bluesky_identifier,
            "github_handle": profile.github_handle,
            "expertise_entries": [entry.entry_text for entry in expertise_entries],
            "availability_slots": self.availability_service.list_for_profile(profile.id),
        }

    def _profile_for_access_key(self, session: Session, access_key: str) -> ExpertProfile:
        profile = session.scalar(
            select(ExpertProfile).where(
                ExpertProfile.access_key_hash == hash_token(access_key),
                ExpertProfile.deleted_at.is_(None),
            )
        )
        if profile is None:
            raise HTTPException(status_code=404, detail="Expert profile not found for the provided access key")
        return profile

    def _replace_expertise_entries(
        self,
        session: Session,
        profile_id: str,
        expertise_entries: list[str],
    ) -> None:
        session.execute(delete(ExpertiseEntry).where(ExpertiseEntry.expert_profile_id == profile_id))
        session.add_all(
            [
                ExpertiseEntry(
                    id=str(uuid4()),
                    expert_profile_id=profile_id,
                    entry_text=entry.strip(),
                    entry_order=index,
                    is_active=True,
                )
                for index, entry in enumerate(expertise_entries, start=1)
            ]
        )

    def _selected_slot_ids(self, session: Session, profile_id: str) -> list[str]:
        slots = session.scalars(
            select(ExpertAvailabilitySlot).where(
                ExpertAvailabilitySlot.expert_profile_id == profile_id,
                ExpertAvailabilitySlot.is_available.is_(True),
            )
        ).all()
        return [slot.canonical_slot_id for slot in slots]

    def _validate_orcid(self, orcid_id: str | None) -> None:
        if orcid_id is None:
            return
        if not self.orcid_client.validate_orcid(orcid_id) or not self.orcid_client.record_exists(orcid_id):
            raise HTTPException(status_code=422, detail="Invalid ORCID ID")

    def _orcid_status(self, orcid_id: str | None) -> str:
        if orcid_id is None:
            return OrcidValidationStatus.NOT_PROVIDED.value
        return OrcidValidationStatus.VERIFIED.value

    @staticmethod
    def _new_token() -> str:
        return secrets.token_urlsafe(24)
