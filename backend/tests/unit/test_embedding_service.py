import math

import pytest
import torch

from app.core.config import Settings, get_settings
from app.services.embedding_service import EmbeddingService


def test_specter2_query_and_document_embeddings_are_normalized():
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
    assert service.query_embedding_label().endswith("allenai/specter2_adhoc_query")
    assert service.document_embedding_label().endswith("allenai/specter2")


def test_specter2_long_text_embedding_matches_manual_chunk_average():
    settings = Settings(
        embedding_provider="specter2",
        embedding_model_name="allenai/specter2_base",
        embedding_document_adapter_name="allenai/specter2",
        embedding_query_adapter_name="allenai/specter2_adhoc_query",
        embedding_dimension=768,
        embedding_chunk_token_limit=128,
        embedding_chunk_token_overlap=32,
        embedding_max_sequence_length=512,
        embedding_cache_dir=get_settings().embedding_cache_dir,
    )
    service = EmbeddingService(settings)
    text = " ".join(f"token-{index}" for index in range(1, 600))

    tokenizer, model = service._specter2_components(
        service.model_name,
        service.document_adapter_name,
        service.cache_dir,
    )
    encoded = service._prepare_specter2_batch(tokenizer, text)
    assert encoded["input_ids"].shape[0] > 1

    with torch.no_grad():
        outputs = model(**encoded)
    chunk_vectors = outputs.last_hidden_state[:, 0, :]
    averaged = chunk_vectors.mean(dim=0)
    manual_vector = averaged / averaged.norm(p=2)

    service_vector = torch.tensor(service.embed_document(text))

    assert service_vector.tolist() == pytest.approx(manual_vector.tolist(), rel=1e-5, abs=1e-6)
