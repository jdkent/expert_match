from __future__ import annotations

import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import DiscoverabilityStatus
from app.models.expert_profile import ExpertProfile
from app.models.publication_record import ExpertSearchDocument


class RetrievalService:
    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
        right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
        return numerator / (left_norm * right_norm)

    def rank_documents(
        self,
        *,
        session: Session,
        query_vector: list[float],
        similarity_threshold: float,
        allowed_source_types: list[str],
    ) -> list[tuple[ExpertProfile, ExpertSearchDocument, float]]:
        if session.bind is None or session.bind.dialect.name != "postgresql":
            raise RuntimeError("RetrievalService requires PostgreSQL with pgvector")
        return self._rank_documents_postgres(
            session=session,
            query_vector=query_vector,
            similarity_threshold=similarity_threshold,
            allowed_source_types=allowed_source_types,
        )

    def _base_statement(self, *, allowed_source_types: list[str]):
        return select(ExpertProfile, ExpertSearchDocument).join(
            ExpertSearchDocument,
            ExpertSearchDocument.expert_profile_id == ExpertProfile.id,
        ).where(
            ExpertProfile.discoverability_status == DiscoverabilityStatus.ACTIVE.value,
            ExpertProfile.deleted_at.is_(None),
            ExpertSearchDocument.is_active.is_(True),
            ExpertSearchDocument.source_type.in_(allowed_source_types),
        )

    def _rank_documents_postgres(
        self,
        *,
        session: Session,
        query_vector: list[float],
        similarity_threshold: float,
        allowed_source_types: list[str],
    ) -> list[tuple[ExpertProfile, ExpertSearchDocument, float]]:
        distance = ExpertSearchDocument.embedding_vector.cosine_distance(query_vector)
        rows = session.execute(
            self._base_statement(allowed_source_types=allowed_source_types)
            .add_columns(distance.label("distance"))
            .where(distance <= 1 - similarity_threshold)
            .order_by(distance.asc())
        ).all()
        return [
            (profile, document, round(1 - float(distance_value), 4))
            for profile, document, distance_value in rows
        ]
