import math

import pytest

from app.core.config import (
    DEFAULT_EMBEDDING_MODEL_NAME,
    DEFAULT_EMBEDDING_PROVIDER,
    Settings,
    get_settings,
)
from app.services.embedding_service import EmbeddingService


def test_mpnet_query_and_document_embeddings_are_normalized():
    settings = get_settings()
    service = EmbeddingService(settings)

    query_vector = service.embed_query("how should I organize my neuroimaging data?")
    document_vector = service.embed_document(
        "Reproducible neuroimaging data organization and metadata workflows."
    )

    assert len(query_vector) == settings.embedding_dimension
    assert len(document_vector) == settings.embedding_dimension
    assert math.isclose(sum(value * value for value in query_vector), 1.0, rel_tol=1e-5)
    assert math.isclose(sum(value * value for value in document_vector), 1.0, rel_tol=1e-5)
    assert service.query_embedding_label() == DEFAULT_EMBEDDING_MODEL_NAME
    assert service.document_embedding_label() == DEFAULT_EMBEDDING_MODEL_NAME


def test_mpnet_defaults_use_model_window():
    settings = get_settings()
    service = EmbeddingService(settings)

    assert settings.embedding_provider == DEFAULT_EMBEDDING_PROVIDER
    assert settings.embedding_model_name == DEFAULT_EMBEDDING_MODEL_NAME
    assert settings.embedding_max_sequence_length == 384
    assert settings.embedding_chunk_token_limit == 382
    assert service.max_sequence_length == 384
    assert service.chunk_token_limit == 382


def test_mpnet_long_text_embedding_matches_manual_chunk_average():
    settings = Settings(
        embedding_provider="sentence-transformers",
        embedding_model_name="sentence-transformers/all-mpnet-base-v2",
        embedding_dimension=768,
        embedding_chunk_token_limit=128,
        embedding_chunk_token_overlap=32,
        embedding_max_sequence_length=384,
        embedding_cache_dir=get_settings().embedding_cache_dir,
    )
    service = EmbeddingService(settings)
    text = " ".join(f"token-{index}" for index in range(1, 600))

    tokenizer, model = service._sentence_transformer_components(service.model_name, service.cache_dir)
    chunk_texts = service._chunk_texts(tokenizer, text)
    assert len(chunk_texts) > 1

    chunk_vectors = model.encode(
        chunk_texts,
        normalize_embeddings=False,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    averaged = chunk_vectors.mean(axis=0)
    length = math.sqrt(float((averaged * averaged).sum()))
    manual_vector = (averaged / length).tolist()
    service_vector = service.embed_document(text)

    assert service_vector == pytest.approx(manual_vector, rel=1e-5, abs=1e-6)
