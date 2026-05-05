QR Code Generator Service

Bu proje, Bulut Mimarilerinde Test Mühendisliği dersi kapsamında
Konu 35: QR Code Generator Service başlığıyla geliştirilmiştir.

🚀 Proje Özeti

Bu servis, kullanıcıdan alınan metni QR koda dönüştürür, çıktıları PNG ve SVG formatlarında saklar ve bu dosyaların indirilmesini sağlar. Ayrıca her QR kod için indirme sayısı gibi üst veriler veritabanında tutulur.

✨ Özellikler
FastAPI tabanlı REST API
Basit ve tek sayfa web arayüzü
PNG ve SVG formatında QR üretimi
İndirme sayısı takibi (hit_count)
LocalStack S3 ve local storage fallback desteği
Docker Compose ve Kubernetes uyumu
CI/CD süreci (GitHub Actions)
Çok katmanlı test yapısı:
Unit: pytest
Entegrasyon: pytest + testcontainers
E2E: Playwright
Performans: k6
🧱 Teknoloji Seçimleri
Katman	Teknoloji	Gerekçe
API	FastAPI	Yüksek performans, tip güvenliği
ORM	SQLAlchemy	Esnek ve güçlü veri modeli
Veritabanı	PostgreSQL	Güvenilir ilişkisel yapı
Depolama	LocalStack S3	S3 davranışını yerelde simüle etme
Test	pytest	Basit ve güçlü test altyapısı
E2E	Playwright	Gerçek kullanıcı senaryoları
Performans	k6	Yük testi ve metrik analizi
Monitoring	Prometheus + Grafana	Gözlemlenebilirlik
🔄 Mimari Akış
Kullanıcı API veya UI üzerinden veri gönderir
Veri Pydantic ile doğrulanır
QR kod (PNG + SVG) üretilir
Dosyalar depolama katmanına yazılır
Üst veri veritabanına kaydedilir
İndirme isteğinde dosya storage’dan okunur
hit_count her indirmede artırılır

📌 Not:
LocalStack erişilemezse sistem otomatik olarak local_storage/ klasörüne geçer.

🔌 API Endpointleri
GET    /
GET    /health
POST   /api/v1/qrcodes
GET    /api/v1/qrcodes
GET    /api/v1/qrcodes/{qr_id}
GET    /api/v1/qrcodes/{qr_id}/download?format=png
GET    /api/v1/qrcodes/{qr_id}/download?format=svg
GET    /api/v1/qrcodes/preview
DELETE /api/v1/qrcodes/{qr_id}
📁 Proje Yapısı
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
⚙️ Kurulum
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m playwright install chromium
▶️ Çalıştırma
Yerel geliştirme
uvicorn src.main:app --host 127.0.0.1 --port 8000
Docker ile
docker compose up --build
Servisler
App → http://localhost:8000
Grafana → http://localhost:3000
Prometheus → http://localhost:9090
LocalStack → http://localhost:4566
🧪 Testler
Tüm testler
pytest --cov=src --cov-report=term-missing --cov-fail-under=70
Unit
pytest tests/unit
Entegrasyon
S3_ENDPOINT_URL=http://localhost:4566 pytest tests/integration -m integration
E2E
E2E_BASE_URL=http://127.0.0.1:8000 pytest tests/e2e/test_qr_ui.py -q
Performans
docker run --rm -v "$PWD:/work" -w /work grafana/k6 run -e BASE_URL=http://host.docker.internal:8000 perf/load-test.js
☸️ Kubernetes
minikube start --driver=docker
docker compose build app
docker tag bmtm-qr-code-generator-app:latest qr-code-generator:local
minikube image load qr-code-generator:local

kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

kubectl rollout status deployment/qr-code-generator --timeout=180s
minikube service qr-code-generator --url
📚 Dokümantasyon

docs/ klasöründe proje çıktıları yer alır:

final-report.pdf → Proje raporu
slides.pdf → Sunum
demo-runbook.md → Demo akışı
final-checklist.md → Teslim kontrol listesi
