"""Veritabanı modelleri."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class QRCodeAsset(Base):
    """Üretilen QR kayıtlarının üst verisini saklar."""

    __tablename__ = "qr_code_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    storage_bucket: Mapped[str] = mapped_column(String(120), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    svg_storage_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, default="image/png")
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
