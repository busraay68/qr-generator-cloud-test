"""Ana uygulama giriş noktası."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import get_settings
from src.db import init_db
from src.routes import qrcodes
from src.services.storage_service import StorageService

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_application() -> FastAPI:
    """FastAPI uygulamasını oluşturur."""

    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db()
        try:
            StorageService.from_settings(settings).ensure_bucket()
        except Exception as exc:  # noqa: BLE001
            # Uygulama açılışı, depolama servisi hazır olmasa da devam eder.
            logger.warning("S3 bucket hazırlama atlandı: %s", exc)
        yield

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        summary="QR kod ureten, S3'e kaydeden ve metadata tutan mini servis",
        lifespan=lifespan,
    )

    if settings.metrics_enabled:
        # Prometheus metrikleri uygulama içinden yayınlanır.
        Instrumentator().instrument(app).expose(app)

    @app.get("/", response_class=HTMLResponse, tags=["ui"])
    def index(request: Request):
        """Ana arayüzü döndürür."""

        return templates.TemplateResponse(
            name="index.html",
            context={
                "request": request,
                "app_name": settings.app_name,
            },
            request=request
        )

    @app.get("/health", tags=["ops"])
    def healthcheck():
        """Servisin sağlık bilgisini döndürür."""

        storage_service = StorageService.from_settings(settings)
        storage_service.ensure_bucket()

        return {
            "status": "ok",
            "service": settings.app_name,
            "environment": settings.app_env,
            "bucket": settings.s3_bucket_name,
            "storage_ready": True,
            "storage_backend": storage_service.backend,
        }

    app.include_router(qrcodes.router)
    return app


app = create_application()
