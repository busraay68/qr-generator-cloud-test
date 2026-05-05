"""Playwright ile tarayıcı seviyesi testler."""

import os
import re
from contextlib import contextmanager

import pytest

pytestmark = pytest.mark.e2e
playwright = pytest.importorskip("playwright.sync_api")


@contextmanager
def open_page():
    """Tarayıcı bağlamını açar ve test sonunda kapatır."""

    base_url = os.getenv("E2E_BASE_URL")
    if not base_url:
        pytest.skip("E2E_BASE_URL tanımlı değil. Deploy sonrası bu test çalıştırılır.")

    with playwright.sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(base_url, wait_until="networkidle")
        try:
            yield page
        finally:
            browser.close()


def create_sample_qr(page, text="https://example.com/e2e", label="e2e-demo"):
    """Arayüz üzerinden örnek bir QR kaydı oluşturur."""

    page.locator("#text-input").fill(text)
    page.locator("#label-input").fill(label)
    page.locator("#create-button").click()
    playwright.expect(page.locator("#status")).to_contain_text("başarıyla")


def test_homepage_shows_initial_state():
    """Ana sayfanın ilk durumda beklenen alanları gösterdiğini doğrular."""

    with open_page() as page:
        playwright.expect(page.locator("h1")).to_contain_text("QR Code Generator")
        playwright.expect(page.locator("#preview-empty")).to_contain_text("Önizleme hazır")
        playwright.expect(page.locator("#char-count")).to_contain_text("0 / 512")


def test_preview_updates_while_typing():
    """Kullanıcı yazdıkça önizleme alanının güncellendiğini doğrular."""

    with open_page() as page:
        page.locator("#text-input").fill("https://example.com/preview")
        playwright.expect(page.locator("#preview-status")).to_contain_text("Önizleme güncel")
        playwright.expect(page.locator("#qr-preview")).to_have_attribute(
            "src", re.compile(r"/api/v1/qrcodes/preview")
        )


def test_user_can_create_qr_code_from_web_ui():
    """Kullanıcının arayüzden QR oluşturabildiğini doğrular."""

    with open_page() as page:
        create_sample_qr(page)
        playwright.expect(page.locator("#qr-preview")).to_be_visible()
        playwright.expect(page.locator("#history")).to_contain_text("e2e-demo")
        playwright.expect(page.locator("#download-png-link")).to_have_attribute(
            "href", re.compile(r"format=png")
        )
        playwright.expect(page.locator("#download-svg-link")).to_have_attribute(
            "href", re.compile(r"format=svg")
        )


def test_reset_button_clears_form_and_preview_state():
    """Temizle düğmesinin formu ve önizleme durumunu sıfırladığını doğrular."""

    with open_page() as page:
        create_sample_qr(page, text="https://example.com/reset", label="reset-deneme")
        page.locator("#reset-button").click()

        playwright.expect(page.locator("#text-input")).to_have_value("")
        playwright.expect(page.locator("#label-input")).to_have_value("")
        playwright.expect(page.locator("#preview-empty")).to_contain_text("Önizleme hazır")
        playwright.expect(page.locator("#preview-hit-count")).to_contain_text("0 kez")


def test_download_links_increment_hit_count():
    """İndirme bağlantılarının sayaç bilgisini artırdığını doğrular."""

    with open_page() as page:
        create_sample_qr(page, text="https://example.com/hit", label="hit-deneme")
        png_url = page.locator("#download-png-link").get_attribute("href")
        svg_url = page.locator("#download-svg-link").get_attribute("href")

        assert png_url is not None
        assert svg_url is not None

        page.goto(png_url, wait_until="networkidle")
        page.go_back(wait_until="networkidle")
        page.goto(svg_url, wait_until="networkidle")
        page.go_back(wait_until="networkidle")
        page.reload(wait_until="networkidle")

        playwright.expect(page.locator("#history")).to_contain_text("2 indirme")
