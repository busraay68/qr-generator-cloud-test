"""QR kod uç noktaları."""

from typing import Literal

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.dependencies import get_qr_code_service, get_session_dependency
from src.schemas import QRCodeCreate, QRCodeRead
from src.services.qr_code_service import QRCodeService
from src.services.qr_generator import generate_qr_png

router = APIRouter(prefix="/api/v1/qrcodes", tags=["qrcodes"])


def _to_response_model(record, request: Request) -> QRCodeRead:
    """Veritabanı kaydını API yanıt modeline dönüştürür."""

    return QRCodeRead(
        id=record.id,
        text=record.text,
        label=record.label,
        storage_bucket=record.storage_bucket,
        storage_key=record.storage_key,
        content_type=record.content_type,
        checksum=record.checksum,
        size_bytes=record.size_bytes,
        hit_count=record.hit_count,
        created_at=record.created_at,
        download_url=f"{request.url_for('download_qr_code', qr_id=record.id)}?format=png",
        svg_download_url=f"{request.url_for('download_qr_code', qr_id=record.id)}?format=svg",
    )


@router.post("", response_model=QRCodeRead, status_code=status.HTTP_201_CREATED)
def create_qr_code(
    payload: QRCodeCreate,
    request: Request,
    session: Session = Depends(get_session_dependency),
    qr_code_service: QRCodeService = Depends(get_qr_code_service),
):
    """Yeni bir QR kaydı oluşturur."""

    record = qr_code_service.create_qr_code(session=session, payload=payload)
    return _to_response_model(record, request)


@router.get("/preview")
def preview_qr_code(
    text: str,
    error_correction: str = "M",
    fill_color: str = "#0f172a",
    background_color: str = "#ffffff",
):
    """Veritabanına yazmadan önizleme görseli üretir."""

    payload = generate_qr_png(
        text=text,
        error_correction=error_correction,
        fill_color=fill_color,
        background_color=background_color,
    )
    return Response(content=payload, media_type="image/png")


@router.get("", response_model=list[QRCodeRead])
def list_qr_codes(
    request: Request,
    session: Session = Depends(get_session_dependency),
    qr_code_service: QRCodeService = Depends(get_qr_code_service),
):
    """Tüm QR kayıtlarını listeler."""

    records = qr_code_service.list_qr_codes(session=session)
    return [_to_response_model(record, request) for record in records]


@router.get("/{qr_id}", response_model=QRCodeRead)
def get_qr_code(
    qr_id: str,
    request: Request,
    session: Session = Depends(get_session_dependency),
    qr_code_service: QRCodeService = Depends(get_qr_code_service),
):
    """Tek bir QR kaydını döndürür."""

    record = qr_code_service.get_qr_code(session=session, qr_id=qr_id)
    return _to_response_model(record, request)


@router.get("/{qr_id}/download", name="download_qr_code")
def download_qr_code(
    qr_id: str,
    format: Literal["png", "svg"] = "png",
    session: Session = Depends(get_session_dependency),
    qr_code_service: QRCodeService = Depends(get_qr_code_service),
):
    """QR dosyasını uygulama üzerinden akış olarak döndürür."""

    record, payload, content_type = qr_code_service.download_qr_code(
        session=session,
        qr_id=qr_id,
        fmt=format,
    )
    extension = "png" if format == "png" else "svg"
    headers = {"Content-Disposition": f'attachment; filename="{record.label}.{extension}"'}
    return StreamingResponse(iter([payload]), media_type=content_type, headers=headers)


@router.delete("/{qr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_qr_code(
    qr_id: str,
    session: Session = Depends(get_session_dependency),
    qr_code_service: QRCodeService = Depends(get_qr_code_service),
):
    """Bir QR kaydını siler."""

    qr_code_service.delete_qr_code(session=session, qr_id=qr_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
