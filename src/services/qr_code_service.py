"""QR kayıt servisi."""

from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models import QRCodeAsset
from src.schemas import QRCodeCreate
from src.services.qr_generator import build_storage_key, generate_qr_png, generate_qr_svg, sha256_hex
from src.services.storage_service import StorageService


class QRCodeService:
    """QR üretim ve kayıt akışını yönetir."""

    def __init__(self, storage_service: StorageService) -> None:
        self.storage_service = storage_service

    def create_qr_code(self, session: Session, payload: QRCodeCreate) -> QRCodeAsset:
        """QR çıktısını üretir, depolar ve veritabanına kaydeder."""

        qr_id = str(uuid4())
        label = payload.label or "generated-qr"
        image_bytes = generate_qr_png(
            text=payload.text,
            error_correction=payload.error_correction,
            fill_color=payload.fill_color,
            background_color=payload.background_color,
        )
        svg_bytes = generate_qr_svg(
            text=payload.text,
            error_correction=payload.error_correction,
            fill_color=payload.fill_color,
            background_color=payload.background_color,
        )
        storage_key = build_storage_key(qr_id=qr_id, label=label, extension="png")
        svg_storage_key = build_storage_key(qr_id=qr_id, label=label, extension="svg")
        self.storage_service.upload_object(
            object_key=storage_key,
            payload=image_bytes,
            content_type="image/png",
        )
        self.storage_service.upload_object(
            object_key=svg_storage_key,
            payload=svg_bytes,
            content_type="image/svg+xml",
        )

        try:
            record = QRCodeAsset(
                id=qr_id,
                text=payload.text,
                label=label,
                storage_bucket=self.storage_service.bucket_name,
                storage_key=storage_key,
                svg_storage_key=svg_storage_key,
                content_type="image/png",
                checksum=sha256_hex(image_bytes),
                size_bytes=len(image_bytes),
                hit_count=0,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except SQLAlchemyError:
            # Veritabanı kaydı başarısız olursa yüklenen dosyalar geri alınır.
            session.rollback()
            self.storage_service.delete(object_key=storage_key)
            self.storage_service.delete(object_key=svg_storage_key)
            raise

    def list_qr_codes(self, session: Session) -> list[QRCodeAsset]:
        """QR kayıtlarını yeni tarihten eski tarihe sıralar."""

        query = select(QRCodeAsset).order_by(QRCodeAsset.created_at.desc())
        return list(session.scalars(query))

    def get_qr_code(self, session: Session, qr_id: str) -> QRCodeAsset:
        """Tek bir QR kaydını döndürür."""

        record = session.get(QRCodeAsset, qr_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{qr_id} id'li QR kod bulunamadi.",
            )
        return record

    def download_qr_code(self, session: Session, qr_id: str, fmt: str = "png") -> tuple[QRCodeAsset, bytes, str]:
        """QR dosyasını indirir ve indirme sayısını günceller."""

        record = self.get_qr_code(session=session, qr_id=qr_id)
        object_key = record.storage_key if fmt == "png" else record.svg_storage_key
        if object_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{fmt} formatı bu kayıt için bulunamadı.",
            )
        downloaded = self.storage_service.download(object_key=object_key)
        record.hit_count += 1
        session.add(record)
        session.commit()
        session.refresh(record)
        return record, downloaded.body, downloaded.content_type

    def delete_qr_code(self, session: Session, qr_id: str) -> None:
        """QR kaydını ve bağlı dosyaları siler."""

        record = self.get_qr_code(session=session, qr_id=qr_id)
        self.storage_service.delete(object_key=record.storage_key)
        if record.svg_storage_key:
            self.storage_service.delete(object_key=record.svg_storage_key)
        session.delete(record)
        session.commit()
