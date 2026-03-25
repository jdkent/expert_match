from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache

from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings, get_settings


def database_is_configured(settings: Settings | None = None) -> bool:
    current_settings = settings or get_settings()
    return bool(current_settings.postgres_dsn)


@lru_cache
def get_engine(dsn: str) -> Engine:
    engine = create_engine(dsn, pool_pre_ping=True)
    if engine.dialect.name == "postgresql":
        @event.listens_for(engine, "connect")
        def _register_pgvector(dbapi_connection, connection_record):  # pragma: no cover - event hook
            register_vector(dbapi_connection)

        ensure_pgvector_extension(engine)
    return engine


def ensure_pgvector_extension(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def get_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    current_settings = settings or get_settings()
    if not current_settings.postgres_dsn:
        raise RuntimeError("POSTGRES_DSN must be configured")
    return sessionmaker(bind=get_engine(current_settings.postgres_dsn))


def check_database_connection(settings: Settings | None = None) -> bool:
    current_settings = settings or get_settings()
    if not current_settings.postgres_dsn:
        return False
    engine = get_engine(current_settings.postgres_dsn)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


@asynccontextmanager
async def get_session():
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
