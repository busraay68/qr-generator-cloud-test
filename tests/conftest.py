"""Pytest fixture'ları."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.db import Base, build_engine, build_session_factory, get_db_session
from src.dependencies import get_storage_service
from src.main import app
from tests.helpers import FakeStorageService


@pytest.fixture
def fake_storage() -> FakeStorageService:
    """Bellek içi sahte depolama servisi döndürür."""

    return FakeStorageService()


@pytest.fixture
def session_factory(tmp_path: Path):
    """İzole bir SQLite session factory üretir."""

    database_path = tmp_path / "unit-test.db"
    engine = build_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    factory = build_session_factory(engine)
    try:
        yield factory
    finally:
        engine.dispose()


@pytest.fixture
def session(session_factory):
    """Ham veritabanı oturumu döndürür."""

    db = session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session_factory, fake_storage):
    """Test istemcisini bağımlılık override'ları ile hazırlar."""

    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_storage_service] = lambda: fake_storage

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
