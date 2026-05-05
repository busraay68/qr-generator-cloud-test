# Final Report

## 1. Giriş

Bu proje, `Bulut Mimarilerinde Test Mühendisliği` dersi kapsamında `Konu 35: QR Code Generator Service` için geliştirilmiştir. Uygulamanın amacı, kullanıcıdan alınan metni QR koda dönüştürmek, üretilen dosyaları bulut benzeri bir depolama katmanında saklamak ve kayıt üst verisini veritabanında tutmaktır. Projenin odak noktası yalnızca QR üretmek değildir; aynı zamanda test edilebilirlik, container tabanlı geliştirme, gözlemlenebilirlik ve dağıtım süreçlerinin uçtan uca gösterilmesidir.

Konu seçimi özellikle sade bir alan modeli sunduğu için tercih edilmiştir. Böylece iş kurallarının karmaşıklığı yerine test piramidi, CI/CD, object storage kullanımı ve Kubernetes dağıtımı gibi dersin teknik hedeflerine ağırlık verilebilmiştir.

## 2. Mimari

Sistem beş ana bileşenden oluşmaktadır:

- `FastAPI` tabanlı uygulama katmanı
- `PostgreSQL` veritabanı
- `LocalStack S3` object storage katmanı
- `Prometheus` ve `Grafana` izleme bileşenleri
- `Docker Compose` ve `Minikube` tabanlı çalışma ortamı

İş akışı şu şekildedir:

1. Kullanıcı arayüzden veya API üzerinden metin gönderir.
2. Uygulama isteği `Pydantic` ile doğrular.
3. `PNG` ve `SVG` biçiminde iki ayrı QR çıktısı üretilir.
4. Çıktılar object storage katmanına yüklenir.
5. QR kaydı, dosya anahtarları ve özet bilgiler PostgreSQL veritabanına yazılır.
6. Kullanıcıya indirme bağlantıları döndürülür.
7. Dosya indirme işlemlerinde `hit_count` alanı artırılır.

Bu yapı sayesinde büyük boyutlu ikili dosyalar veritabanında tutulmaz; veritabanı sadece sorgulanabilir üst veriyi saklar. Böylece uygulama katmanı ile depolama katmanı ayrışmış olur.

## 3. Test Stratejisi

Proje, farklı seviyelerde testler içerecek şekilde hazırlanmıştır:

### Unit Testler

Unit testler `tests/unit/` altında yer alır. Bu katmanda:

- QR üretim yardımcıları
- servis katmanı
- API route davranışları
- depolama servisinin yerel fallback modu

doğrulanmaktadır.

### Integration Testler

Integration testler `tests/integration/` altında yer alır. Bu testler:

- `testcontainers` kullanarak gerçek PostgreSQL container davranışını
- `LocalStack S3` üzerinden object storage roundtrip akışını

doğrular.

### E2E Testler

E2E testleri `Playwright` ile yazılmıştır. Testler arayüz üzerinde:

- ana sayfanın ilk görünümünü
- canlı önizleme davranışını
- QR oluşturma akışını
- form sıfırlama davranışını
- indirme sayacı güncellemesini

kontrol eder.

### Coverage Sonucu

Backend test paketi tekrar çalıştırıldığında toplam coverage değeri `%88.19` olarak ölçülmüştür. Böylece şartnamedeki `%70` eşiği rahat biçimde aşılmıştır.

## 4. Pipeline ve Dağıtım

GitHub Actions workflow dosyası `.github/workflows/ci.yml` altında yer alır. Pipeline akışı şu sırayı izler:

`lint -> pytest -> docker build -> kubernetes deploy -> smoke test -> e2e -> newman -> k6`

Bu akış sayesinde kod kalitesi, testler, container build, Kubernetes deploy ve son kullanıcıya yakın doğrulamalar tek zincirde birleştirilmiştir.

Yerel geliştirme için `docker-compose.yml` kullanılmaktadır. Bu yapı içinde uygulama, PostgreSQL, LocalStack, Prometheus ve Grafana birlikte ayağa kalkar. Kubernetes tarafında ise aynı servisler Minikube üzerinde `deployment`, `service` ve `configmap` manifestleri ile çalıştırılır.

## 5. Performans ve Gözlemlenebilirlik

Uygulama `Prometheus FastAPI Instrumentator` ile `/metrics` uç noktasından metrik üretmektedir. Grafana dashboard içinde üç temel panel vardır:

- Throughput
- p95 Latency
- Error Rate

Performans testi `k6` ile `POST /api/v1/qrcodes` uç noktası üzerinde çalıştırılmıştır. Son ölçümde:

- `p95 latency = 262.72 ms`
- hata oranı `0.00%`
- toplam istek sayısı `251`

olarak gözlenmiştir. Tanımlı eşik `p(95) < 800 ms` olduğu için senaryo başarıyla geçmiştir.

## 6. Sonuç

Bu proje, küçük bir servis üzerinde dahi bulut mimarisi ilkeleri ile test mühendisliği pratiklerinin birlikte uygulanabileceğini göstermektedir. QR üretim alanı sade tutulmuş; buna karşılık test çeşitliliği, container kullanımı, object storage entegrasyonu, CI/CD, monitoring ve Kubernetes dağıtımı güçlü biçimde ele alınmıştır.

Proje sonunda elde edilen temel kazanımlar şunlardır:

- iş mantığını servis katmanında toplamanın test yazımını kolaylaştırdığı
- object storage ile veritabanı sorumluluklarını ayırmanın doğru bir mimari tercih olduğu
- LocalStack ve testcontainers ile bulut benzeri senaryoların yerel ortamda tekrar üretilebildiği
- E2E, Newman ve k6 gibi araçların farklı kalite katmanlarını görünür hale getirdiği

Bu nedenle proje, dersin teknik beklentilerini karşılamaktadır
