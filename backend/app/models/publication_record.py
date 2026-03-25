from __future__ import annotations

from datetime import date
from uuid import uuid4

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Boolean, Date, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import DEFAULT_EMBEDDING_MODEL_NAME
from app.db.base import Base


EMBEDDING_VECTOR_DIMENSIONS = 768


class PublicationRecord(Base):
    __tablename__ = "publication_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    external_work_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(512))
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    author_position: Mapped[str] = mapped_column(String(16))
    author_priority: Mapped[str] = mapped_column(String(16))
    abstract_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    abstract_status: Mapped[str] = mapped_column(String(32))
    selected_for_enrichment: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ExpertSearchDocument(Base):
    __tablename__ = "expert_search_documents"
    __table_args__ = (
        Index(
            "ix_expert_search_documents_current_embedding_vector_hnsw",
            "embedding_vector",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding_vector": "vector_cosine_ops"},
            postgresql_where=text(
                f"is_active = true AND embedding_model = '{DEFAULT_EMBEDDING_MODEL_NAME}'"
            ),
        ),
        Index(
            "ix_expert_search_documents_current_manual_embedding_vector_hnsw",
            "embedding_vector",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding_vector": "vector_cosine_ops"},
            postgresql_where=text(
                f"source_type = 'manual_expertise' AND is_active = true AND embedding_model = '{DEFAULT_EMBEDDING_MODEL_NAME}'"
            ),
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    expert_profile_id: Mapped[str] = mapped_column(String, index=True)
    source_type: Mapped[str] = mapped_column(String(32))
    source_record_id: Mapped[str] = mapped_column(String, index=True)
    document_text: Mapped[str] = mapped_column(Text)
    embedding_vector: Mapped[list[float]] = mapped_column(VECTOR(EMBEDDING_VECTOR_DIMENSIONS))
    embedding_model: Mapped[str] = mapped_column(String(255), default=DEFAULT_EMBEDDING_MODEL_NAME)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
