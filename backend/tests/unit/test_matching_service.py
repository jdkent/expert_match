from app.core.config import Settings
from app.db.session import database_is_configured
from tests.helpers import create_expert


def test_matching_service_deduplicates_experts(client):
    create_expert(
        client,
        full_name="Ada Lovelace",
        email="ada@example.org",
        expertise_entries=["Metadata workflows", "Reproducible research"],
    )
    payload = client.post(
        "/api/v1/match-queries",
        json={
            "query_text": "reproducible research metadata",
        },
    ).json()
    assert len(payload["matches"]) == 1


def test_database_configuration_detects_dsn():
    assert database_is_configured(Settings(POSTGRES_DSN="postgresql+psycopg://example")) is True
    assert database_is_configured(Settings(POSTGRES_DSN=None)) is False
