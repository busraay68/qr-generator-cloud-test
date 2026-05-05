"""Test veri fabrikaları."""

from datetime import UTC, datetime

import factory
from faker import Faker

from src.models import QRCodeAsset

fake = Faker("tr_TR")


class QRCodeAssetFactory(factory.Factory):
    """ORM oturumuna bağlı olmayan QR kayıt fabrikası."""

    class Meta:
        model = QRCodeAsset

    id = factory.Faker("uuid4")
    text = factory.LazyFunction(lambda: fake.url())
    label = factory.LazyFunction(lambda: fake.slug())
    storage_bucket = "test-bucket"
    storage_key = factory.LazyAttribute(lambda obj: f"qrcodes/test/{obj.id}.png")
    svg_storage_key = factory.LazyAttribute(lambda obj: f"qrcodes/test/{obj.id}.svg")
    content_type = "image/png"
    checksum = factory.Faker("sha256")
    size_bytes = 1024
    hit_count = 0
    created_at = factory.LazyFunction(lambda: datetime.now(UTC))
