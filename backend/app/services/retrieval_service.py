from __future__ import annotations

from dataclasses import dataclass
import math
import re

from sqlalchemy import func, literal, or_, select
from sqlalchemy.orm import Session

from app.models.enums import DiscoverabilityStatus
from app.models.expert_profile import ExpertProfile
from app.models.publication_record import ExpertSearchDocument


@dataclass(frozen=True)
class RankedDocument:
    profile: ExpertProfile
    document: ExpertSearchDocument
    score: float


class RetrievalService:
    LEXICAL_CANDIDATE_MULTIPLIER = 4
    MIN_LEXICAL_CANDIDATES = 100
    TRIGRAM_QUERY_TOKEN_LIMIT = 8
    TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
        right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
        return numerator / (left_norm * right_norm)

    def rank_semantic_documents(
        self,
        *,
        session: Session,
        query_vector: list[float],
        allowed_source_types: list[str],
        embedding_model: str,
        limit: int,
    ) -> list[RankedDocument]:
        if session.bind is None or session.bind.dialect.name != "postgresql":
            raise RuntimeError("RetrievalService requires PostgreSQL with pgvector")
        return self._rank_semantic_documents_postgres(
            session=session,
            query_vector=query_vector,
            allowed_source_types=allowed_source_types,
            embedding_model=embedding_model,
            limit=limit,
        )

    def rank_lexical_documents(
        self,
        *,
        session: Session,
        query_text: str,
        allowed_source_types: list[str],
        limit: int,
    ) -> list[RankedDocument]:
        if session.bind is None or session.bind.dialect.name != "postgresql":
            raise RuntimeError("RetrievalService requires PostgreSQL with pg_trgm and full-text search")
        return self._rank_lexical_documents_postgres(
            session=session,
            query_text=query_text,
            allowed_source_types=allowed_source_types,
            limit=limit,
        )

    def _base_statement(
        self,
        *,
        allowed_source_types: list[str],
        embedding_model: str | None = None,
    ):
        statement = select(ExpertProfile, ExpertSearchDocument).join(
            ExpertSearchDocument,
            ExpertSearchDocument.expert_profile_id == ExpertProfile.id,
        ).where(
            ExpertProfile.discoverability_status == DiscoverabilityStatus.ACTIVE.value,
            ExpertProfile.deleted_at.is_(None),
            ExpertSearchDocument.is_active.is_(True),
            ExpertSearchDocument.source_type.in_(allowed_source_types),
        )
        if embedding_model is not None:
            statement = statement.where(ExpertSearchDocument.embedding_model == embedding_model)
        return statement

    def _rank_semantic_documents_postgres(
        self,
        *,
        session: Session,
        query_vector: list[float],
        allowed_source_types: list[str],
        embedding_model: str,
        limit: int,
    ) -> list[RankedDocument]:
        distance = ExpertSearchDocument.embedding_vector.cosine_distance(query_vector)
        rows = session.execute(
            self._base_statement(
                allowed_source_types=allowed_source_types,
                embedding_model=embedding_model,
            )
            .add_columns(distance.label("distance"))
            .order_by(distance.asc())
            .limit(limit)
        ).all()
        return [
            RankedDocument(
                profile=profile,
                document=document,
                score=round(1 - float(distance_value), 4),
            )
            for profile, document, distance_value in rows
        ]

    def _rank_lexical_documents_postgres(
        self,
        *,
        session: Session,
        query_text: str,
        allowed_source_types: list[str],
        limit: int,
    ) -> list[RankedDocument]:
        document_text, document_tsvector, tsquery = self._text_search_parts(query_text)
        lowered_document_text, lowered_query_text, trigram_similarity, trigram_word_similarity = (
            self._trigram_parts(document_text=document_text, query_text=query_text)
        )
        ts_rank = func.ts_rank_cd(document_tsvector, tsquery)
        lexical_score = (
            ts_rank * 0.8
            + func.greatest(trigram_similarity, trigram_word_similarity) * 0.2
        )
        candidate_limit = max(limit * self.LEXICAL_CANDIDATE_MULTIPLIER, self.MIN_LEXICAL_CANDIDATES)
        fts_candidate_ids = session.scalars(
            self._base_statement(allowed_source_types=allowed_source_types)
            .with_only_columns(ExpertSearchDocument.id)
            .where(document_tsvector.op("@@")(tsquery))
            .order_by(ts_rank.desc())
            .limit(candidate_limit)
        ).all()
        trigram_candidate_ids: list[str] = []
        if self._should_run_trigram(
            query_text=query_text,
            fts_candidate_count=len(fts_candidate_ids),
            limit=limit,
        ):
            trigram_candidate_ids = session.scalars(
                self._base_statement(allowed_source_types=allowed_source_types)
                .with_only_columns(ExpertSearchDocument.id)
                .where(
                    or_(
                        lowered_document_text.bool_op("%")(lowered_query_text),
                        literal(lowered_query_text).bool_op("<%")(lowered_document_text),
                    )
                )
                .order_by(
                    trigram_similarity.desc(),
                    trigram_word_similarity.desc(),
                )
                .limit(candidate_limit)
            ).all()
        candidate_ids = list(dict.fromkeys([*fts_candidate_ids, *trigram_candidate_ids]))
        if not candidate_ids:
            return []
        rows = session.execute(
            self._base_statement(allowed_source_types=allowed_source_types)
            .add_columns(lexical_score.label("lexical_score"))
            .where(ExpertSearchDocument.id.in_(candidate_ids))
            .order_by(
                lexical_score.desc(),
                ts_rank.desc(),
                trigram_similarity.desc(),
                trigram_word_similarity.desc(),
            )
            .limit(limit)
        ).all()
        return [
            RankedDocument(
                profile=profile,
                document=document,
                score=round(float(score_value), 4),
            )
            for profile, document, score_value in rows
        ]

    @staticmethod
    def _text_search_parts(query_text: str):
        document_text = func.coalesce(ExpertSearchDocument.document_text, "")
        document_tsvector = func.to_tsvector("english", document_text)
        tsquery = func.websearch_to_tsquery("english", query_text)
        return document_text, document_tsvector, tsquery

    @staticmethod
    def _trigram_parts(*, document_text, query_text: str):
        lowered_document_text = func.lower(document_text)
        lowered_query_text = query_text.lower()
        trigram_similarity = func.similarity(lowered_document_text, lowered_query_text)
        trigram_word_similarity = func.word_similarity(lowered_query_text, lowered_document_text)
        return lowered_document_text, lowered_query_text, trigram_similarity, trigram_word_similarity

    @classmethod
    def _should_run_trigram(
        cls,
        *,
        query_text: str,
        fts_candidate_count: int,
        limit: int,
    ) -> bool:
        if fts_candidate_count >= limit:
            return False
        return len(cls._normalized_tokens(query_text)) <= cls.TRIGRAM_QUERY_TOKEN_LIMIT

    @classmethod
    def _normalized_tokens(cls, text: str) -> set[str]:
        return set(cls.TOKEN_PATTERN.findall(text.lower()))
