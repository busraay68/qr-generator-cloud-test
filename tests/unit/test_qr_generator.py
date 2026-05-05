"""QR üretim yardımcı testleri."""

from src.services.qr_generator import (
    build_storage_key,
    generate_qr_png,
    generate_qr_svg,
    normalize_hex_color,
    resolve_error_correction,
    sha256_hex,
)


def test_generate_qr_png_returns_png_signature():
    """PNG çıktısının beklenen imza ile başladığını doğrular."""

    payload = generate_qr_png("https://marmara.edu.tr")
    assert payload.startswith(b"\x89PNG")
    assert len(payload) > 200


def test_generate_qr_png_supports_custom_color_and_error_correction():
    """Renk ve hata düzeltme seçeneklerinin işlendiğini doğrular."""

    payload = generate_qr_png(
        "https://example.com/pro",
        error_correction="H",
        fill_color="#2563eb",
        background_color="#ffffff",
    )
    assert payload.startswith(b"\x89PNG")


def test_generate_qr_svg_returns_svg_markup():
    """SVG çıktısının XML ya da SVG işareti içerdiğini doğrular."""

    payload = generate_qr_svg("https://example.com/vector", error_correction="Q")
    assert payload.startswith(b"<?xml") or b"<svg" in payload


def test_build_storage_key_sanitizes_label():
    """Depolama anahtarında etiketin güvenli biçime çevrildiğini doğrular."""

    storage_key = build_storage_key("abc-123", "Örnek Demo QR!")
    svg_key = build_storage_key("abc-123", "Örnek Demo QR!", extension="svg")
    assert storage_key.endswith("abc-123-ornek-demo-qr.png")
    assert svg_key.endswith("abc-123-ornek-demo-qr.svg")
    assert storage_key.startswith("qrcodes/")


def test_sha256_hex_is_deterministic():
    """Aynı giriş için aynı özet değerinin üretildiğini doğrular."""

    assert sha256_hex(b"demo") == sha256_hex(b"demo")


def test_color_and_error_correction_helpers_normalize_values():
    """Yardımcı fonksiyonların beklenen dönüşümleri yaptığını doğrular."""

    assert normalize_hex_color("#ABCDEF") == "#abcdef"
    assert resolve_error_correction("Q") > 0
