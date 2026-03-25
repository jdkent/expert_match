from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MATCH_ACCEPTANCE_THRESHOLD = 0.51
DEFAULT_LEXICAL_SEARCH_TOP_K = 50
DEFAULT_SEMANTIC_SEARCH_TOP_K = 25
DEFAULT_RRF_K = 15
LEGACY_EMBEDDING_MODEL_NAME = "allenai/specter2"
DEFAULT_EMBEDDING_PROVIDER = "sentence-transformers"
DEFAULT_EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
DEFAULT_EMBEDDING_DIMENSION = 768
DEFAULT_EMBEDDING_MAX_SEQUENCE_LENGTH = 384
DEFAULT_EMBEDDING_CHUNK_TOKEN_LIMIT = 382


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,
        populate_by_name=True,
    )

    env: str = "development"
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    match_acceptance_threshold: float = Field(
        default=DEFAULT_MATCH_ACCEPTANCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices(
            "match_acceptance_threshold",
            "similarity_threshold",
            "MATCH_ACCEPTANCE_THRESHOLD",
            "SIMILARITY_THRESHOLD",
            "APP_MATCH_ACCEPTANCE_THRESHOLD",
            "APP_SIMILARITY_THRESHOLD",
        ),
    )
    lexical_search_top_k: int = Field(default=DEFAULT_LEXICAL_SEARCH_TOP_K, ge=25, le=100)
    semantic_search_top_k: int = Field(default=DEFAULT_SEMANTIC_SEARCH_TOP_K, ge=10, le=50)
    rrf_k: int = Field(default=DEFAULT_RRF_K, ge=1, le=500)
    embedding_dimension: int = Field(default=DEFAULT_EMBEDDING_DIMENSION, ge=8, le=2048)
    embedding_provider: str = DEFAULT_EMBEDDING_PROVIDER
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL_NAME
    embedding_cache_dir: str = "/tmp/expert-match-model-cache"
    embedding_max_sequence_length: int = Field(default=DEFAULT_EMBEDDING_MAX_SEQUENCE_LENGTH, ge=32, le=4096)
    embedding_chunk_token_limit: int = Field(default=DEFAULT_EMBEDDING_CHUNK_TOKEN_LIMIT, ge=16, le=4096)
    embedding_chunk_token_overlap: int = Field(default=64, ge=0, le=1024)
    orcid_base_url: str = "https://pub.orcid.org/v3.0"
    orcid_live_validation: bool = True
    orcid_timeout_seconds: float = Field(default=20.0, gt=0.0, le=120.0)
    openalex_base_url: str = "https://api.openalex.org"
    openalex_enabled: bool = True
    openalex_email: str = "jamesdkent21@gmail.com"
    openalex_api_key: str | None = None
    openalex_timeout_seconds: float = Field(default=20.0, gt=0.0, le=120.0)
    search_include_publication_abstracts: bool = True
    postgres_dsn: str | None = Field(
        default=None,
        validation_alias=AliasChoices("postgres_dsn", "POSTGRES_DSN", "APP_POSTGRES_DSN"),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
