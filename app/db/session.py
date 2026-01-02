from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_engine = None
_session_local = None


def _get_sessionmaker():
    global _engine, _session_local
    if _session_local is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _session_local = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    return _session_local


def get_db():
    SessionLocal = _get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
