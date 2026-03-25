from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions, sessionmaker

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import ensure_pgvector_extension
from app.models import *  # noqa: F403
from app.main import app


@pytest.fixture(scope="session")
def engine():
    settings = get_settings()
    engine = create_engine(settings.postgres_dsn, pool_pre_ping=True)
    ensure_pgvector_extension(engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    close_all_sessions()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_connection(engine) -> Iterator:
    connection = engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        close_all_sessions()
        transaction.rollback()
        connection.close()


@pytest.fixture
def session_factory(db_connection) -> Iterator[sessionmaker]:
    yield sessionmaker(bind=db_connection, join_transaction_mode="create_savepoint")


@pytest.fixture
def client(session_factory) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        for service_name in ("availability", "expert_profile", "matching", "outreach"):
            app.state.services[service_name].session_factory = session_factory
        yield test_client


@pytest.fixture
def vcr_config():
    return {
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "once",
        "filter_headers": ["authorization"],
        "filter_query_parameters": ["mailto", "api_key"],
        "decode_compressed_response": True,
    }
