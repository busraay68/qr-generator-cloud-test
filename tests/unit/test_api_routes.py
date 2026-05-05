"""API uç noktası testleri."""


def test_full_api_lifecycle(client):
    """Oluşturma, listeleme, indirme ve silme akışını doğrular."""

    create_response = client.post(
        "/api/v1/qrcodes",
        json={
            "text": "https://example.com/demo",
            "label": "demo-link",
            "error_correction": "H",
            "fill_color": "#1d4ed8",
            "background_color": "#ffffff",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["download_url"].endswith(f'/api/v1/qrcodes/{created["id"]}/download?format=png')
    assert created["svg_download_url"].endswith(
        f'/api/v1/qrcodes/{created["id"]}/download?format=svg'
    )

    list_response = client.get("/api/v1/qrcodes")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    detail_response = client.get(f'/api/v1/qrcodes/{created["id"]}')
    assert detail_response.status_code == 200
    assert detail_response.json()["label"] == "demo-link"
    assert detail_response.json()["hit_count"] == 0

    download_response = client.get(f'/api/v1/qrcodes/{created["id"]}/download')
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "image/png"
    assert download_response.content.startswith(b"\x89PNG")

    svg_download_response = client.get(f'/api/v1/qrcodes/{created["id"]}/download?format=svg')
    assert svg_download_response.status_code == 200
    assert svg_download_response.headers["content-type"] == "image/svg+xml"
    assert b"<svg" in svg_download_response.content

    refreshed_detail_response = client.get(f'/api/v1/qrcodes/{created["id"]}')
    assert refreshed_detail_response.json()["hit_count"] == 2

    delete_response = client.delete(f'/api/v1/qrcodes/{created["id"]}')
    assert delete_response.status_code == 204

    not_found_response = client.get(f'/api/v1/qrcodes/{created["id"]}')
    assert not_found_response.status_code == 404


def test_create_qr_code_rejects_empty_text(client):
    """Boş metin isteğinin doğrulama katmanında reddedildiğini doğrular."""

    response = client.post("/api/v1/qrcodes", json={"text": "", "label": "bos"})
    assert response.status_code == 422


def test_preview_endpoint_returns_rendered_qr(client):
    """Önizleme uç noktasının PNG görsel döndürdüğünü doğrular."""

    response = client.get(
        "/api/v1/qrcodes/preview",
        params={
            "text": "preview-demo",
            "error_correction": "Q",
            "fill_color": "#0f766e",
            "background_color": "#ffffff",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")


def test_health_endpoint_reports_service_state(client):
    """Sağlık uç noktasının temel servis bilgisini döndürdüğünü doğrular."""

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["storage_backend"] in {"s3", "local"}
