# Performans Raporu

Bu dosya, `p95 latency` ölçümü ve yorumları için ayrılmıştır.

## Test Konfigürasyonu

- Araç: `k6`
- VU: `10`
- Süre: `30 saniye`
- Endpoint: `POST /api/v1/qrcodes`

## Ölçülen Sonuçlar

- p95 latency: `262.72 ms`
- Ortalama istek süresi: `195.22 ms`
- Hata oranı: `0.00%`
- Toplam istek: `251`
- En yüksek gözlenen istek süresi: `340.17 ms`

## Teknik Yorum

- QR üretimi CPU ağırlıklı ama kısa süreli bir işlemdir.
- En büyük dış bağımlılık S3 yükleme adımıdır.
- p95 değeri yükselirse ilk bakılacak yerler `LocalStack erişimi`, `DB yazma süresi` ve `container kaynak limiti` olmalıdır.
- Ölçüm, `grafana/k6` container'ı üzerinden `host.docker.internal:8000` hedefi için alınmıştır.
- Mevcut sonuçlar, tanımlı `p(95)<800 ms` eşiğinin rahat biçimde sağlandığını göstermektedir.
