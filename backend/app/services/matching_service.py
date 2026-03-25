from __future__ import annotations

from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.models.enums import DiscoverabilityStatus, SearchStatus
from app.models.expert_profile import ExpertProfile
from app.models.expert_query import ExpertQuery, MatchResult
from app.models.publication_record import ExpertSearchDocument
from app.models.enums import SourceType
from app.schemas.matching import MatchQueryInput
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService


class MatchingService:
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        settings: Settings,
        embedding_service: EmbeddingService,
        retrieval_service: RetrievalService,
    ) -> None:
        self.session_factory = session_factory
        self.settings = settings
        self.embedding_service = embedding_service
        self.retrieval_service = retrieval_service

    def create_match_query(self, payload: MatchQueryInput) -> dict:
        query_id = str(uuid4())
        query_vector = self.embedding_service.embed_query(payload.query_text)
        with self.session_factory() as session:
            try:
                query = ExpertQuery(
                    id=query_id,
                    requester_contact_id=None,
                    query_text=payload.query_text,
                    query_embedding_vector=query_vector,
                    embedding_model=self.embedding_service.query_embedding_label(),
                    similarity_threshold=self.settings.similarity_threshold,
                    search_status=SearchStatus.READY.value,
                )
                session.add(query)
                session.flush()

                rows = self.retrieval_service.rank_documents(
                    session=session,
                    query_vector=query_vector,
                    similarity_threshold=self.settings.similarity_threshold,
                    allowed_source_types=self._allowed_source_types(),
                )

                expert_best_matches: dict[str, dict] = {}
                for profile, document, score in rows:
                    existing = expert_best_matches.get(profile.id)
                    if existing is not None and existing["aggregate_similarity_score"] >= score:
                        continue
                    expert_best_matches[profile.id] = {
                        "expert_profile_id": profile.id,
                        "expert_search_document_id": document.id,
                        "aggregate_similarity_score": round(score, 4),
                        "top_document_similarity_score": round(score, 4),
                        "matched_document_excerpt": document.document_text[:180],
                        "full_name": profile.full_name,
                        "email": profile.email,
                        "website_url": profile.website_url,
                        "x_handle": profile.x_handle,
                        "linkedin_identifier": profile.linkedin_identifier,
                        "bluesky_identifier": profile.bluesky_identifier,
                        "github_handle": profile.github_handle,
                    }

                ranked = sorted(
                    expert_best_matches.values(),
                    key=lambda item: item["aggregate_similarity_score"],
                    reverse=True,
                )[:5]

                session.execute(delete(MatchResult).where(MatchResult.expert_query_id == query_id))
                for index, match in enumerate(ranked, start=1):
                    session.add(
                        MatchResult(
                            id=str(uuid4()),
                            expert_query_id=query_id,
                            expert_profile_id=match["expert_profile_id"],
                            expert_search_document_id=match["expert_search_document_id"],
                            rank_position=index,
                            expert_similarity_score=match["aggregate_similarity_score"],
                            top_document_similarity_score=match["top_document_similarity_score"],
                            match_explanation=f"Matched on document excerpt: {match['matched_document_excerpt']}",
                        )
                    )
                session.commit()
            except Exception:
                session.rollback()
                raise

        return {
            "match_query_id": query_id,
            "applied_similarity_threshold": self.settings.similarity_threshold,
            "matches": [
                {
                    "expert_id": match["expert_profile_id"],
                    "full_name": match["full_name"],
                    "email": match["email"],
                    "aggregate_similarity_score": match["aggregate_similarity_score"],
                    "matched_document_excerpt": match["matched_document_excerpt"],
                    "website_url": match["website_url"],
                    "x_handle": match["x_handle"],
                    "linkedin_identifier": match["linkedin_identifier"],
                    "bluesky_identifier": match["bluesky_identifier"],
                    "github_handle": match["github_handle"],
                }
                for match in ranked
            ],
        }

    def _allowed_source_types(self) -> list[str]:
        allowed_source_types = [SourceType.MANUAL_EXPERTISE.value]
        if self.settings.search_include_publication_abstracts:
            allowed_source_types.append(SourceType.PUBLICATION_ABSTRACT.value)
        return allowed_source_types
