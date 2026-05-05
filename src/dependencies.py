"""FastAPI bağımlılıkları."""

from fastapi import Depends
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.db import get_db_session
from src.services.qr_code_service import QRCodeService
from src.services.storage_service import StorageService


def get_settings_dependency() -> Settings:
    """Uygulama ayarlarını döndürür."""

    return get_settings()


def get_storage_service(
    settings: Settings = Depends(get_settings_dependency),
) -> StorageService:
    """Depolama servisini oluşturur."""

    return StorageService.from_settings(settings)


def get_qr_code_service(
    storage_service: StorageService = Depends(get_storage_service),
) -> QRCodeService:
    """QR iş mantığı servisini oluşturur."""

    return QRCodeService(storage_service=storage_service)


def get_session_dependency(session: Session = Depends(get_db_session)) -> Session:
    """Veritabanı oturumunu döndürür."""

    return session
