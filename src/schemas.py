"""İstek ve yanıt şemaları."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class QRCodeCreate(BaseModel):
    """QR üretim isteği."""

    text: str = Field(min_length=1, max_length=512, description="QR koda cevrilecek ana metin")
    label: str | None = Field(
        default=None,
        max_length=80,
        description="Dosya adı ve arayüz gösterimi için kullanılan kısa etiket",
    )
    error_correction: Literal["L", "M", "Q", "H"] = Field(
        default="M",
        description="QR kodun hata düzeltme seviyesi",
    )
    fill_color: str = Field(
        default="#0f172a",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="QR kodun ana rengi",
    )
    background_color: str = Field(
        default="#ffffff",
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="QR kodun arka plan rengi",
    )


class QRCodeRead(BaseModel):
    """QR kaydı için API yanıtı."""

    id: str
    text: str
    label: str
    storage_bucket: str
    storage_key: str
    content_type: str
    checksum: str
    size_bytes: int
    hit_count: int
    created_at: datetime
    download_url: str
    svg_download_url: str

    model_config = {"from_attributes": True}
