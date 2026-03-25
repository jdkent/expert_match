from __future__ import annotations

import math
from functools import lru_cache

import torch
from adapters import AutoAdapterModel
from transformers import AutoTokenizer

from app.core.config import Settings

class EmbeddingService:
    def __init__(self, settings: Settings) -> None:
        self.dimension = settings.embedding_dimension
        self.provider = settings.embedding_provider
        self.model_name = settings.embedding_model_name
        self.document_adapter_name = settings.embedding_document_adapter_name
        self.query_adapter_name = settings.embedding_query_adapter_name
        self.cache_dir = settings.embedding_cache_dir
        self.max_sequence_length = settings.embedding_max_sequence_length
        self.chunk_token_limit = min(settings.embedding_chunk_token_limit, settings.embedding_max_sequence_length - 2)
        self.chunk_token_overlap = min(settings.embedding_chunk_token_overlap, self.chunk_token_limit - 1)
        if self.provider != "specter2":
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def embed_text(self, text: str) -> list[float]:
        return self.embed_document(text)

    def document_embedding_label(self) -> str:
        return self._embedding_label(self.document_adapter_name)

    def query_embedding_label(self) -> str:
        return self._embedding_label(self.query_adapter_name)

    def embed_document(self, text: str) -> list[float]:
        return self._specter2_embedding(text, adapter_name=self.document_adapter_name)

    def embed_query(self, text: str) -> list[float]:
        return self._specter2_embedding(text, adapter_name=self.query_adapter_name)

    def _specter2_embedding(self, text: str, *, adapter_name: str) -> list[float]:
        return list(
            self._cached_specter2_embedding(
                self.model_name,
                adapter_name,
                self.cache_dir,
                self.max_sequence_length,
                self.chunk_token_limit,
                self.chunk_token_overlap,
                text.strip() or "empty",
            )
        )

    def _embedding_label(self, adapter_name: str) -> str:
        return f"{self.model_name}:{adapter_name}"

    def _prepare_specter2_batch(self, tokenizer: AutoTokenizer, text: str) -> dict[str, torch.Tensor]:
        unknown_token_id = tokenizer.unk_token_id or 0
        token_ids = tokenizer(text, add_special_tokens=False, truncation=False)["input_ids"] or [unknown_token_id]
        stride = max(1, self.chunk_token_limit - self.chunk_token_overlap)
        chunks = []
        for start_index in range(0, len(token_ids), stride):
            chunk = token_ids[start_index : start_index + self.chunk_token_limit]
            if not chunk:
                continue
            prepared_chunk = tokenizer.prepare_for_model(
                chunk,
                add_special_tokens=True,
                truncation=True,
                max_length=self.max_sequence_length,
                padding=False,
                return_attention_mask=True,
                return_token_type_ids=False,
            )
            chunks.append(prepared_chunk)
            if start_index + self.chunk_token_limit >= len(token_ids):
                break
        return tokenizer.pad(chunks, padding=True, return_tensors="pt")

    @staticmethod
    @lru_cache(maxsize=4)
    def _specter2_components(
        model_name: str,
        adapter_name: str,
        cache_dir: str,
    ) -> tuple[AutoTokenizer, AutoAdapterModel]:
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = AutoAdapterModel.from_pretrained(model_name, cache_dir=cache_dir)
        loaded_adapter_name = model.load_adapter(adapter_name, source="hf", set_active=True)
        model.set_active_adapters(loaded_adapter_name)
        model.eval()
        return tokenizer, model

    @staticmethod
    @lru_cache(maxsize=2048)
    def _cached_specter2_embedding(
        model_name: str,
        adapter_name: str,
        cache_dir: str,
        max_sequence_length: int,
        chunk_token_limit: int,
        chunk_token_overlap: int,
        text: str,
    ) -> tuple[float, ...]:
        tokenizer, model = EmbeddingService._specter2_components(model_name, adapter_name, cache_dir)
        service = EmbeddingService.__new__(EmbeddingService)
        service.max_sequence_length = max_sequence_length
        service.chunk_token_limit = chunk_token_limit
        service.chunk_token_overlap = chunk_token_overlap
        encoded = service._prepare_specter2_batch(tokenizer, text)
        with torch.no_grad():
            outputs = model(**encoded)
        chunk_vectors = outputs.last_hidden_state[:, 0, :]
        averaged = chunk_vectors.mean(dim=0)
        vector = averaged.tolist()
        length = math.sqrt(sum(value * value for value in vector)) or 1.0
        return tuple(float(value) / length for value in vector)
