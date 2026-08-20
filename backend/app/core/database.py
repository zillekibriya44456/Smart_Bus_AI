"""
Database engine, session factory, and health-check helper.

The SQLAlchemy engine is created lazily so the application can be imported
(and tested) without a PostgreSQL driver being present.
"""
import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from .config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

_engine = None
_SessionLocal = None


def _get_engine():
    """Lazily create the SQLAlchemy engine on first access."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
        )
    return _engine


# Keep the public name 'engine' so existing imports continue to work
@property
def engine():
    return _get_engine()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Returns True if the database is reachable, False otherwise.
    Used by the /health endpoint.
    """
    try:
        with _get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        return False
