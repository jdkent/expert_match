from __future__ import annotations

from uuid import uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import DEFAULT_EMBEDDING_MODEL_NAME, DEFAULT_SIMILARITY_THRESHOLD
from app.db.base import Base
from app.models.publication_record import EMBEDDING_VECTOR_DIMENSIONS


class ExpertQuery(Base):
    __tablename__ = "expert_queries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    requester_contact_id: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    query_text: Mapped[str] = mapped_column(Text)
    query_embedding_vector: Mapped[list[float]] = mapped_column(VECTOR(EMBEDDING_VECTOR_DIMENSIONS))
    embedding_model: Mapped[str] = mapped_column(String(255), default=DEFAULT_EMBEDDING_MODEL_NAME)
    similarity_threshold: Mapped[float] = mapped_column(Float, default=DEFAULT_SIMILARITY_THRESHOLD)
    search_status: Mapped[str] = mapped_column(String(32), default="pending")


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_query_id: Mapped[str] = mapped_column(String, index=True)
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    expert_search_document_id: Mapped[str] = mapped_column(String, index=True)
    rank_position: Mapped[int]
    expert_similarity_score: Mapped[float] = mapped_column(Float)
    top_document_similarity_score: Mapped[float] = mapped_column(Float)
    match_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
