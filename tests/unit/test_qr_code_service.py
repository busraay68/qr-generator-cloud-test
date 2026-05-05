"""QR servis testi."""

import pytest
from fastapi import HTTPException

from src.schemas import QRCodeCreate
from src.services.qr_code_service import QRCodeService
from tests.helpers import FakeStorageService


def test_create_qr_code_persists_metadata_and_uploads_to_storage(session):
    """Oluşturma işleminin hem veritabanına hem depolamaya yazdığını doğrular."""

    storage = FakeStorageService()
    service = QRCodeService(storage_service=storage)

    record = service.create_qr_code(
        session=session,
        payload=QRCodeCreate(text="Örnek QR içeriği", label="ornek-qr"),
    )

    assert record.id
    assert record.storage_bucket == "test-bucket"
    assert record.storage_key in storage.objects
    assert record.svg_storage_key in storage.objects
    assert record.size_bytes == len(storage.objects[record.storage_key])


def test_download_qr_code_returns_binary_payload(session):
    """PNG indirme akışını doğrular."""

    storage = FakeStorageService()
    service = QRCodeService(storage_service=storage)
    created = service.create_qr_code(
        session=session,
        payload=QRCodeCreate(text="download testi", label="indir"),
    )

    record, payload, content_type = service.download_qr_code(session=session, qr_id=created.id)

    assert record.id == created.id
    assert payload.startswith(b"\x89PNG")
    assert content_type == "image/png"
    assert record.hit_count == 1


def test_download_qr_code_supports_svg_format(session):
    """SVG indirme akışını doğrular."""

    storage = FakeStorageService()
    service = QRCodeService(storage_service=storage)
    created = service.create_qr_code(
        session=session,
        payload=QRCodeCreate(text="svg testi", label="vektor"),
    )

    record, payload, content_type = service.download_qr_code(
        session=session,
        qr_id=created.id,
        fmt="svg",
    )

    assert record.id == created.id
    assert b"<svg" in payload
    assert content_type == "image/svg+xml"
    assert record.hit_count == 1


def test_delete_qr_code_removes_db_row_and_storage_object(session):
    """Silme işleminin hem veriyi hem dosyaları kaldırdığını doğrular."""

    storage = FakeStorageService()
    service = QRCodeService(storage_service=storage)
    created = service.create_qr_code(
        session=session,
        payload=QRCodeCreate(text="delete testi", label="sil"),
    )

    service.delete_qr_code(session=session, qr_id=created.id)

    assert created.storage_key not in storage.objects
    with pytest.raises(HTTPException):
        service.get_qr_code(session=session, qr_id=created.id)
