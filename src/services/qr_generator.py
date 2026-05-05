"""QR üretim yardımcıları."""

import hashlib
import re
import unicodedata
from datetime import UTC, datetime
from io import BytesIO
from typing import Literal

import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q
from qrcode.image.svg import SvgPathImage

ERROR_CORRECTION_LEVELS = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def normalize_hex_color(color: str) -> str:
    """Renk değerini `#RRGGBB` biçimine doğrular."""

    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Renk değeri #RRGGBB formatında olmalıdır.")
    return color.lower()


def resolve_error_correction(level: Literal["L", "M", "Q", "H"]) -> int:
    """Hata düzeltme seviyesini kütüphane sabitine çevirir."""

    return ERROR_CORRECTION_LEVELS[level]


def generate_qr_png(
    text: str,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    fill_color: str = "#0f172a",
    background_color: str = "#ffffff",
) -> bytes:
    """PNG biçiminde QR görseli üretir."""

    normalized_fill = normalize_hex_color(fill_color)
    normalized_background = normalize_hex_color(background_color)

    qr = qrcode.QRCode(
        version=None,
        error_correction=resolve_error_correction(error_correction),
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    image = qr.make_image(fill_color=normalized_fill, back_color=normalized_background)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_qr_svg(
    text: str,
    error_correction: Literal["L", "M", "Q", "H"] = "M",
    fill_color: str = "#111111",
    background_color: str = "#ffffff",
) -> bytes:
    """SVG biçiminde QR görseli üretir."""

    normalized_fill = normalize_hex_color(fill_color)
    normalized_background = normalize_hex_color(background_color)

    qr = qrcode.QRCode(
        version=None,
        error_correction=resolve_error_correction(error_correction),
        box_size=10,
        border=4,
        image_factory=SvgPathImage,
    )
    qr.add_data(text)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color=normalized_fill,
        back_color=normalized_background,
    )
    buffer = BytesIO()
    image.save(buffer)
    return buffer.getvalue()


def build_storage_key(qr_id: str, label: str, extension: str = "png") -> str:
    """Depolama anahtarını tarih tabanlı klasör yapısı ile üretir."""

    normalized_label = (
        unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode("ascii")
    )
    safe_label = re.sub(r"[^a-zA-Z0-9]+", "-", normalized_label).strip("-").lower() or "qr-code"
    day_path = datetime.now(UTC).strftime("%Y/%m/%d")
    return f"qrcodes/{day_path}/{qr_id}-{safe_label}.{extension}"


def sha256_hex(payload: bytes) -> str:
    """Verilen içerik için SHA-256 özeti üretir."""

    return hashlib.sha256(payload).hexdigest()
