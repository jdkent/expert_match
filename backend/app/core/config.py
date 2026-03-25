from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SIMILARITY_THRESHOLD = 0.75


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        case_sensitive=False,
        populate_by_name=True,
    )

    env: str = "development"
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    similarity_threshold: float = Field(default=DEFAULT_SIMILARITY_THRESHOLD, ge=0.0, le=1.0)
    embedding_dimension: int = Field(default=768, ge=8, le=2048)
    embedding_provider: str = "specter2"
    embedding_model_name: str = "allenai/specter2_base"
    embedding_document_adapter_name: str = "allenai/specter2"
    embedding_query_adapter_name: str = "allenai/specter2_adhoc_query"
    embedding_cache_dir: str = "/tmp/expert-match-model-cache"
    embedding_max_sequence_length: int = Field(default=512, ge=32, le=4096)
    embedding_chunk_token_limit: int = Field(default=510, ge=16, le=4096)
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
