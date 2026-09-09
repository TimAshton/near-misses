import os

os.environ.setdefault("SCHEDULER_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite in-memory for test speed. The `raw` JSON column and Uuid PK are both
# defined with cross-dialect types in models/incident.py specifically so this
# works the same as it does against Postgres in dev/prod.
from near_misses.api import deps
from near_misses.db import Base
from near_misses.main import app


@pytest.fixture()
def db_session():
    # StaticPool: TestClient runs route handlers in a threadpool worker thread,
    # so the engine needs to hand out the SAME connection everywhere, or each
    # thread would see its own empty in-memory database.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
