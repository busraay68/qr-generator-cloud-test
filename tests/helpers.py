"""Test yardımcıları."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from src.services.storage_service import DownloadedObject


class FakeStorageService:
    """Bellek içi depolama taklidi."""

    def __init__(self) -> None:
        self.bucket_name = "test-bucket"
        self.objects: dict[str, bytes] = {}
        self.content_types: dict[str, str] = {}

    def ensure_bucket(self) -> None:
        """Gerçek servis arayüzü ile uyumu korur."""

    def upload_object(self, object_key: str, payload: bytes, content_type: str) -> None:
        self.objects[object_key] = payload
        self.content_types[object_key] = content_type

    def download(self, object_key: str) -> DownloadedObject:
        payload = self.objects[object_key]
        return DownloadedObject(
            body=payload,
            content_type=self.content_types[object_key],
            size_bytes=len(payload),
        )

    def delete(self, object_key: str) -> None:
        self.objects.pop(object_key, None)
        self.content_types.pop(object_key, None)


def session_scope(session_factory) -> Generator[Session, None, None]:
    """Kısa ömürlü bir oturum kapsamı sağlar."""

    session = session_factory()
    try:
        yield session
    finally:
        session.close()
