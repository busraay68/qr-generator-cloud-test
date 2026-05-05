"""Depolama servisi testleri."""

from pathlib import Path

import pytest

from src.services.storage_service import StorageService


def build_storage(tmp_path: Path) -> StorageService:
    """Test için yerel depolama modunda çalışan servis üretir."""

    storage = StorageService(
        bucket_name="test-bucket",
        region_name="us-east-1",
        endpoint_url=None,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        local_storage_dir=tmp_path,
    )
    storage.backend = "local"
    return storage


def test_upload_and_download_roundtrip_on_local_backend(tmp_path):
    """Yerel depolama modunda yazma ve okuma akışını doğrular."""

    storage = build_storage(tmp_path)
    object_key = "qrcodes/2026/05/04/ornek.png"
    payload = b"\x89PNGdemo"

    storage.upload_object(object_key=object_key, payload=payload, content_type="image/png")
    downloaded = storage.download(object_key=object_key)

    assert downloaded.body == payload
    assert downloaded.content_type == "image/png"
    assert downloaded.size_bytes == len(payload)


def test_delete_removes_local_file(tmp_path):
    """Silme işleminin yerel dosyayı kaldırdığını doğrular."""

    storage = build_storage(tmp_path)
    object_key = "qrcodes/2026/05/04/ornek.svg"

    storage.upload_object(object_key=object_key, payload=b"<svg/>", content_type="image/svg+xml")
    storage.delete(object_key=object_key)

    assert not (tmp_path / object_key).exists()


def test_download_missing_local_file_raises_error(tmp_path):
    """Olmayan dosya için uygun dosya sistemi hatasının yükseldiğini doğrular."""

    storage = build_storage(tmp_path)

    with pytest.raises(FileNotFoundError):
        storage.download("qrcodes/2026/05/04/yok.png")
