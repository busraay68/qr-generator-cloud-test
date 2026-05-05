# QR Code Generator Service

Bu proje, `Bulut Mimarilerinde Test Mühendisliği` dersi dönem ödevi için `Konu 35: QR Code Generator Service` başlığı altında hazırlanmıştır.

## Genel Bakış

Uygulama kullanıcıdan aldığı metin için QR kod üretir, dosyaları `PNG` ve `SVG` olarak depolar, kayıt üst verisini veritabanında tutar ve indirme isteklerini uygulama üzerinden sunar.

Öne çıkan özellikler:

- `FastAPI` tabanlı REST API
- Tek sayfa sade web arayüzü
- `PNG` ve `SVG` çıktı desteği
- İndirme sayısı takibi
- `LocalStack S3` ve yerel depolama uyumu
- `PostgreSQL`, `Docker Compose`, `Kubernetes`, `GitHub Actions`
- `pytest`, `Playwright`, `k6`, `Postman/Newman` test akışı

## Teknoloji Tercihleri

| Katman | Seçim | Gerekçe |
|---|---|---|
| API | FastAPI | Tip güvenliği, hızlı geliştirme, kolay test edilebilir yapı |
| Veritabanı | SQLAlchemy + PostgreSQL | İlişkisel üst veri yönetimi ve container uyumu |
| Depolama | LocalStack S3 | S3 davranışını yerelde tekrarlayabilme |
| Unit Test | pytest | Fixture, parametrizasyon ve hızlı geri bildirim |
| Entegrasyon Testi | pytest + testcontainers | Gerçek PostgreSQL davranışını doğrulama |
| E2E Test | Playwright | Tarayıcı seviyesinde kullanıcı akışını doğrulama |
| Performans Testi | k6 | Gecikme ve hata oranı takibi |
| İzleme | Prometheus + Grafana | Metrik toplama ve panel gösterimi |

## Mimari Akış

1. Kullanıcı arayüzden veya API üzerinden içerik gönderir.
2. İstek `Pydantic` ile doğrulanır.
3. Uygulama `PNG` ve `SVG` QR dosyalarını üretir.
4. Dosyalar önce depolama katmanına yazılır.
5. Üst veri veritabanına kaydedilir.
6. İndirme uç noktası dosyayı depolamadan okuyup istemciye iletir.
7. Her indirme işleminde `hit_count` alanı güncellenir.

`LocalStack` erişilemediğinde uygulama otomatik olarak `local_storage/` klasörüne düşer. Böylece geliştirme ve demo akışı kesilmez.

## API İşlemleri

- `GET /`
- `GET /health`
- `POST /api/v1/qrcodes`
- `GET /api/v1/qrcodes`
- `GET /api/v1/qrcodes/{qr_id}`
- `GET /api/v1/qrcodes/{qr_id}/download?format=png`
- `GET /api/v1/qrcodes/{qr_id}/download?format=svg`
- `GET /api/v1/qrcodes/preview`
- `DELETE /api/v1/qrcodes/{qr_id}`

## Proje Yapısı

```text
bmtm-qr-code-generator/
├── .github/workflows/
├── docs/
├── k8s/
├── monitoring/
├── perf/
├── postman/
├── src/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m playwright install chromium
```

## Çalıştırma

Yerel geliştirme:

```bash
source .venv/bin/activate
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Tüm servislerle birlikte:

```bash
docker compose up --build
```

Servis adresleri:

- Uygulama: `http://localhost:8000`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- LocalStack: `http://localhost:4566`

## Testler

Tüm testler:

```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

Unit testler:

```bash
pytest tests/unit
```

Entegrasyon testleri:

```bash
S3_ENDPOINT_URL=http://localhost:4566 pytest tests/integration -m integration
```

E2E testi:

```bash
E2E_BASE_URL=http://127.0.0.1:8000 pytest tests/e2e/test_qr_ui.py -q
```

Performans testi:

```bash
docker run --rm -v "$PWD:/work" -w /work grafana/k6 run -e BASE_URL=http://host.docker.internal:8000 perf/load-test.js
```

## Kubernetes

```bash
minikube start --driver=docker
docker compose build app
docker tag bmtm-qr-code-generator-app:latest qr-code-generator:local
minikube image load qr-code-generator:local
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl rollout status deployment/qr-code-generator --timeout=180s
minikube service qr-code-generator --url
```

## Dokümantasyon

`docs/` klasöründe mimari diyagram, rapor ve slayt dosyaları yer alır.

- `docs/final-report.pdf`: final rapor
- `docs/slides.pdf`: sunum çıktısı
- `docs/demo-runbook.md`: canlı demo ve video akışı
- `docs/final-checklist.md`: teslim öncesi son kontrol listesi
