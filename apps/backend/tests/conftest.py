"""
Pytest test configuration and fixtures for NORMVAULT.
Uses an isolated SQLite database for lightning-fast, reproducible tests.
"""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment before loading config
os.environ["DATABASE_URL"] = "sqlite:///./test_normvault.db"
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "True"

from app.main import app
from app.db.base import Base
from app.db.session import get_db

from sqlalchemy import create_engine, event

test_engine = create_engine(
    "sqlite:///./test_normvault.db",
    connect_args={"check_same_thread": False},
)

@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables before test run and clean up afterwards."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_normvault.db"):
        try:
            os.remove("./test_normvault.db")
        except Exception:
            pass


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provides a fresh transactional database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        try:
            session.rollback()
            for table in reversed(Base.metadata.sorted_tables):
                session.execute(table.delete())
            session.commit()
        except Exception:
            pass
        finally:
            session.close()



@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient that overrides the get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
