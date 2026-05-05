"""PostgreSQL container entegrasyon testleri."""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

docker = pytest.importorskip("docker")
testcontainers_postgres = pytest.importorskip("testcontainers.postgres")

from src.db import Base, build_engine, build_session_factory, get_db_session
from src.dependencies import get_storage_service
from src.main import app
from tests.helpers import FakeStorageService


def _normalize_postgres_url(connection_url: str) -> str:
    """Bağlantı adresini psycopg sürücüsüne uyarlar."""

    if connection_url.startswith("postgresql+psycopg2://"):
        return connection_url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    if connection_url.startswith("postgresql://"):
        return connection_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return connection_url


def _require_docker_daemon() -> None:
    """Docker erişimi yoksa testi atlar."""

    try:
        client = docker.from_env()
        client.ping()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Docker daemon erisilemedi: {exc}")


def test_create_qr_code_against_postgres_container():
    """Oluşturma akışını gerçek PostgreSQL üzerinde doğrular."""

    _require_docker_daemon()
    with testcontainers_postgres.PostgresContainer("postgres:16") as postgres:
        engine = build_engine(_normalize_postgres_url(postgres.get_connection_url()))
        Base.metadata.create_all(engine)
        session_factory = build_session_factory(engine)

        def override_db():
            db = session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db_session] = override_db
        app.dependency_overrides[get_storage_service] = lambda: FakeStorageService()

        with TestClient(app) as client:
            response = client.post(
                "/api/v1/qrcodes",
                json={"text": "postgres integration", "label": "pg-demo"},
            )
            assert response.status_code == 201
            payload = response.json()
            assert payload["label"] == "pg-demo"
            assert payload["storage_bucket"] == "test-bucket"

        app.dependency_overrides.clear()
        engine.dispose()


def test_delete_qr_code_against_postgres_container():
    """Silme akışını gerçek PostgreSQL üzerinde doğrular."""

    _require_docker_daemon()
    with testcontainers_postgres.PostgresContainer("postgres:16") as postgres:
        engine = build_engine(_normalize_postgres_url(postgres.get_connection_url()))
        Base.metadata.create_all(engine)
        session_factory = build_session_factory(engine)
        fake_storage = FakeStorageService()

        def override_db():
            db = session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db_session] = override_db
        app.dependency_overrides[get_storage_service] = lambda: fake_storage

        with TestClient(app) as client:
            created = client.post(
                "/api/v1/qrcodes",
                json={"text": "silinecek kayit", "label": "delete-me"},
            )
            qr_id = created.json()["id"]

            delete_response = client.delete(f"/api/v1/qrcodes/{qr_id}")
            assert delete_response.status_code == 204

            detail_response = client.get(f"/api/v1/qrcodes/{qr_id}")
            assert detail_response.status_code == 404

        app.dependency_overrides.clear()
        engine.dispose()
