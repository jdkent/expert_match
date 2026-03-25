from __future__ import annotations

import math
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

from app.core.config import Settings


class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.dimension = settings.embedding_dimension
        self.provider = settings.embedding_provider
        self.model_name = settings.embedding_model_name
        self.cache_dir = settings.embedding_cache_dir
        self.max_sequence_length = settings.embedding_max_sequence_length
        self.chunk_token_limit = min(
            settings.embedding_chunk_token_limit,
            settings.embedding_max_sequence_length - 2,
        )
        self.chunk_token_overlap = min(settings.embedding_chunk_token_overlap, self.chunk_token_limit - 1)
        if self.provider != "sentence-transformers":
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def embed_text(self, text: str) -> list[float]:
        return self.embed_document(text)

    def document_embedding_label(self) -> str:
        return self._embedding_label()

    def query_embedding_label(self) -> str:
        return self._embedding_label()

    def embed_document(self, text: str) -> list[float]:
        return self._sentence_transformer_embedding(text)

    def embed_query(self, text: str) -> list[float]:
        return self._sentence_transformer_embedding(text)

    def _sentence_transformer_embedding(self, text: str) -> list[float]:
        return list(
            self._cached_sentence_transformer_embedding(
                self.model_name,
                self.cache_dir,
                self.max_sequence_length,
                self.chunk_token_limit,
                self.chunk_token_overlap,
                text.strip() or "empty",
            )
        )

    def _embedding_label(self) -> str:
        return self.model_name

    def _chunk_texts(self, tokenizer: AutoTokenizer, text: str) -> list[str]:
        unknown_token_id = tokenizer.unk_token_id or 0
        token_ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"] or [unknown_token_id]
        stride = max(1, self.chunk_token_limit - self.chunk_token_overlap)
        chunks: list[str] = []
        for start_index in range(0, len(token_ids), stride):
            chunk_token_ids = token_ids[start_index : start_index + self.chunk_token_limit]
            if not chunk_token_ids:
                continue
            chunk_text = tokenizer.decode(
                chunk_token_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            chunks.append(chunk_text.strip() or tokenizer.unk_token or "empty")
            if start_index + self.chunk_token_limit >= len(token_ids):
                break
        return chunks

    @staticmethod
    @lru_cache(maxsize=4)
    def _sentence_transformer_components(
        model_name: str,
        cache_dir: str,
    ) -> tuple[AutoTokenizer, SentenceTransformer]:
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = SentenceTransformer(model_name, cache_folder=cache_dir)
        model.max_seq_length = getattr(model, "max_seq_length", 0) or 384
        return tokenizer, model

    @staticmethod
    @lru_cache(maxsize=2048)
    def _cached_sentence_transformer_embedding(
        model_name: str,
        cache_dir: str,
        max_sequence_length: int,
        chunk_token_limit: int,
        chunk_token_overlap: int,
        text: str,
    ) -> tuple[float, ...]:
        tokenizer, model = EmbeddingService._sentence_transformer_components(model_name, cache_dir)
        model.max_seq_length = min(
            getattr(model, "max_seq_length", max_sequence_length) or max_sequence_length,
            max_sequence_length,
        )
        service = EmbeddingService.__new__(EmbeddingService)
        service.max_sequence_length = max_sequence_length
        service.chunk_token_limit = chunk_token_limit
        service.chunk_token_overlap = chunk_token_overlap
        chunk_texts = service._chunk_texts(tokenizer, text)
        chunk_vectors = model.encode(
            chunk_texts,
            normalize_embeddings=False,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        averaged = chunk_vectors.mean(axis=0)
        vector = averaged.tolist()
        length = math.sqrt(sum(value * value for value in vector)) or 1.0
        return tuple(float(value) / length for value in vector)
