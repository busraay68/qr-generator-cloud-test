"""Uygulama ayarları."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Ortam değişkenlerinden beslenen uygulama ayarları."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "QR Code Generator Service"
    app_env: str = "development"
    database_url: str = "sqlite:///./qr_service.db"
    s3_bucket_name: str = "qr-code-assets"
    s3_region: str = "us-east-1"
    s3_endpoint_url: str | None = "http://localhost:4566"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_session_token: str | None = None
    metrics_enabled: bool = True
    local_storage_dir: Path = Path("./local_storage")


@lru_cache
def get_settings() -> Settings:
    """Ayar nesnesini önbellekten döndürür."""

    return Settings()
