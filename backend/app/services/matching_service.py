from __future__ import annotations

from dataclasses import dataclass
import re
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.models.enums import SearchStatus
from app.models.expert_profile import ExpertProfile
from app.models.expert_query import ExpertQuery, MatchResult
from app.models.publication_record import ExpertSearchDocument
from app.models.enums import SourceType
from app.schemas.matching import MatchQueryInput
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RankedDocument, RetrievalService


@dataclass
class ExpertMatchCandidate:
    profile: ExpertProfile
    lexical_document: ExpertSearchDocument | None = None
    lexical_rank: int | None = None
    lexical_score: float | None = None
    semantic_document: ExpertSearchDocument | None = None
    semantic_rank: int | None = None
    semantic_score: float | None = None

    def raw_rrf_score(self, rrf_k: int) -> float:
        score = 0.0
        if self.lexical_rank is not None:
            score += 1 / (rrf_k + self.lexical_rank)
        if self.semantic_rank is not None:
            score += 1 / (rrf_k + self.semantic_rank)
        return score


class MatchingService:
    TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
    MAX_MATCHES = 5

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
                    match_acceptance_threshold=self.settings.match_acceptance_threshold,
                    search_status=SearchStatus.READY.value,
                )
                session.add(query)
                session.flush()

                lexical_rows = self.retrieval_service.rank_lexical_documents(
                    session=session,
                    query_text=payload.query_text,
                    allowed_source_types=self._allowed_source_types(),
                    limit=self.settings.lexical_search_top_k,
                )
                semantic_rows = self.retrieval_service.rank_semantic_documents(
                    session=session,
                    query_vector=query_vector,
                    allowed_source_types=self._allowed_source_types(),
                    embedding_model=self.embedding_service.query_embedding_label(),
                    limit=self.settings.semantic_search_top_k,
                )

                ranked = self._rank_candidates(
                    query_text=payload.query_text,
                    lexical_rows=lexical_rows,
                    semantic_rows=semantic_rows,
                )

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
                            match_explanation=match["match_explanation"],
                        )
                    )
                session.commit()
            except Exception:
                session.rollback()
                raise

        return {
            "match_query_id": query_id,
            "applied_match_acceptance_threshold": self.settings.match_acceptance_threshold,
            "matches": [
                {
                    "expert_id": match["expert_profile_id"],
                    "full_name": match["full_name"],
                    "email": match["email"],
                    "short_bio": match["short_bio"],
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

    def _rank_candidates(
        self,
        *,
        query_text: str,
        lexical_rows: list[RankedDocument],
        semantic_rows: list[RankedDocument],
    ) -> list[dict]:
        candidates: dict[str, ExpertMatchCandidate] = {}
        self._apply_ranked_rows(
            query_text=query_text,
            ranked_rows=lexical_rows,
            candidates=candidates,
            modality="lexical",
        )
        self._apply_ranked_rows(
            query_text=query_text,
            ranked_rows=semantic_rows,
            candidates=candidates,
            modality="semantic",
        )

        ranked_matches: list[dict] = []
        for candidate in candidates.values():
            raw_rrf_score = candidate.raw_rrf_score(self.settings.rrf_k)
            normalized_rrf_score = self._normalized_rrf_score(raw_rrf_score)
            if normalized_rrf_score < self.settings.match_acceptance_threshold:
                continue
            supporting_document = self._supporting_document(candidate)
            ranked_matches.append(
                {
                    "expert_profile_id": candidate.profile.id,
                    "expert_search_document_id": supporting_document.id,
                    "aggregate_similarity_score": round(normalized_rrf_score, 4),
                    "top_document_similarity_score": round(
                        candidate.semantic_score or normalized_rrf_score,
                        4,
                    ),
                    "matched_document_excerpt": supporting_document.document_text[:180],
                    "full_name": candidate.profile.full_name,
                    "email": candidate.profile.email,
                    "short_bio": candidate.profile.short_bio,
                    "website_url": candidate.profile.website_url,
                    "x_handle": candidate.profile.x_handle,
                    "linkedin_identifier": candidate.profile.linkedin_identifier,
                    "bluesky_identifier": candidate.profile.bluesky_identifier,
                    "github_handle": candidate.profile.github_handle,
                    "match_explanation": self._match_explanation(candidate, supporting_document),
                    "_raw_rrf_score": raw_rrf_score,
                    "_semantic_score": candidate.semantic_score or 0.0,
                    "_lexical_score": candidate.lexical_score or 0.0,
                }
            )

        ranked_matches.sort(
            key=lambda item: (
                item["_raw_rrf_score"],
                item["_semantic_score"],
                item["_lexical_score"],
            ),
            reverse=True,
        )
        return [
            {
                key: value
                for key, value in match.items()
                if not key.startswith("_")
            }
            for match in ranked_matches[: self.MAX_MATCHES]
        ]

    def _apply_ranked_rows(
        self,
        *,
        query_text: str,
        ranked_rows: list[RankedDocument],
        candidates: dict[str, ExpertMatchCandidate],
        modality: str,
    ) -> None:
        for rank, ranked_document in enumerate(ranked_rows, start=1):
            if not self._passes_short_query_lexical_floor(
                query_text=query_text,
                document_text=ranked_document.document.document_text,
            ):
                continue
            candidate = candidates.setdefault(
                ranked_document.profile.id,
                ExpertMatchCandidate(profile=ranked_document.profile),
            )
            if modality == "lexical":
                if candidate.lexical_rank is not None and candidate.lexical_rank <= rank:
                    continue
                candidate.lexical_document = ranked_document.document
                candidate.lexical_rank = rank
                candidate.lexical_score = ranked_document.score
                continue
            if candidate.semantic_rank is not None and candidate.semantic_rank <= rank:
                continue
            candidate.semantic_document = ranked_document.document
            candidate.semantic_rank = rank
            candidate.semantic_score = ranked_document.score

    def _normalized_rrf_score(self, raw_rrf_score: float) -> float:
        max_rrf_score = 2 / (self.settings.rrf_k + 1)
        return min(raw_rrf_score / max_rrf_score, 1.0)

    @staticmethod
    def _supporting_document(candidate: ExpertMatchCandidate) -> ExpertSearchDocument:
        if candidate.lexical_document is None:
            return candidate.semantic_document
        if candidate.semantic_document is None:
            return candidate.lexical_document
        if candidate.lexical_rank <= candidate.semantic_rank:
            return candidate.lexical_document
        return candidate.semantic_document

    @staticmethod
    def _match_explanation(
        candidate: ExpertMatchCandidate,
        supporting_document: ExpertSearchDocument,
    ) -> str:
        evidence: list[str] = []
        if candidate.lexical_rank is not None:
            evidence.append(f"lexical rank {candidate.lexical_rank}")
        if candidate.semantic_rank is not None:
            evidence.append(f"semantic rank {candidate.semantic_rank}")
        joined_evidence = ", ".join(evidence) or "retrieval evidence"
        return f"Matched on {joined_evidence}; excerpt: {supporting_document.document_text[:180]}"

    def _allowed_source_types(self) -> list[str]:
        allowed_source_types = [SourceType.MANUAL_EXPERTISE.value, SourceType.SHORT_BIO.value]
        if self.settings.search_include_publication_abstracts:
            allowed_source_types.append(SourceType.PUBLICATION_ABSTRACT.value)
        return allowed_source_types

    def _passes_short_query_lexical_floor(self, *, query_text: str, document_text: str) -> bool:
        query_tokens = self._normalized_tokens(query_text)
        if len(query_tokens) > self.settings.short_query_token_limit:
            return True
        document_tokens = self._normalized_tokens(document_text)
        return len(query_tokens & document_tokens) >= self.settings.short_query_lexical_overlap_floor

    @classmethod
    def _normalized_tokens(cls, text: str) -> set[str]:
        return set(cls.TOKEN_PATTERN.findall(text.lower()))
