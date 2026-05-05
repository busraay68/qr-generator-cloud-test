"""LocalStack S3 entegrasyon testi."""

import os

import pytest

pytestmark = pytest.mark.integration
pytest.importorskip("boto3")

from src.config import Settings
from src.db import Base, build_engine, build_session_factory
from src.schemas import QRCodeCreate
from src.services.qr_code_service import QRCodeService
from src.services.storage_service import StorageService


def test_localstack_s3_roundtrip(tmp_path):
    """Oluşturulan dosyanın LocalStack üzerinden okunabildiğini doğrular."""

    endpoint_url = os.getenv("S3_ENDPOINT_URL")
    if not endpoint_url:
        pytest.skip("LocalStack endpoint tanımlı değil. CI veya docker-compose ortamında çalıştırın.")

    settings = Settings(
        s3_bucket_name="integration-qr-assets",
        s3_endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    storage_service = StorageService.from_settings(settings)
    storage_service.ensure_bucket()

    engine = build_engine(f"sqlite:///{tmp_path / 'localstack.db'}")
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)

    with session_factory() as session:
        qr_service = QRCodeService(storage_service=storage_service)
        created = qr_service.create_qr_code(
            session=session,
            payload=QRCodeCreate(text="localstack integration", label="localstack-demo"),
        )
        _, payload, content_type = qr_service.download_qr_code(session=session, qr_id=created.id)

        assert payload.startswith(b"\x89PNG")
        assert content_type == "image/png"
        assert created.storage_bucket == "integration-qr-assets"

    engine.dispose()
