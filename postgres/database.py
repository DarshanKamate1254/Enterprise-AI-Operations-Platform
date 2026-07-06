import sys
import os
from contextlib import contextmanager
from typing import Generator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, Session
from config import settings

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# Configure Connection Pooling parameters
# pool_size: number of connections to keep open
# max_overflow: maximum overflow connections allowed when pool is full
# pool_recycle: automatically recycle connections older than 30 mins (1800s)
# pool_pre_ping: test connection health before checking it out
ENGINE_KWARGS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_recycle": 1800,
    "pool_pre_ping": True
}

import os

# Resolve PostgreSQL URL from settings or override with DATABASE_URL
connection_url = os.getenv("DATABASE_URL") or settings.db.connection_url

# We will initialize the engine. Note: For tests, we may override the engine or URL.
if "sqlite" in connection_url:
    # SQLite does not support connection pooling parameters like pool_size
    engine = create_engine(connection_url)
else:
    engine = create_engine(connection_url, **ENGINE_KWARGS)


# Configure the sessionmaker
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Handles automatic commit on success and rollback on exceptions, ensuring transaction isolation.
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
