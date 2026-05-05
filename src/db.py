"""Veritabanı yardımcıları."""

from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import get_settings


class Base(DeclarativeBase):
    """Tüm ORM modellerinin taban sınıfı."""


def build_engine(database_url: str):
    """Verilen bağlantı adresi için SQLAlchemy engine üretir."""

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


def build_session_factory(engine):
    """Session factory üretir."""

    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


settings = get_settings()
engine = build_engine(settings.database_url)
SessionLocal = build_session_factory(engine)


def init_db() -> None:
    """Tabloları oluşturur ve eksik kolonları tamamlar."""

    from src import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_backward_compatible_schema()


def ensure_backward_compatible_schema() -> None:
    """Geliştirme veritabanındaki eksik kolonları ekler."""

    inspector = inspect(engine)
    if "qr_code_assets" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("qr_code_assets")}
    statements: list[str] = []

    if "svg_storage_key" not in existing_columns:
        statements.append("ALTER TABLE qr_code_assets ADD COLUMN svg_storage_key VARCHAR(255)")
    if "hit_count" not in existing_columns:
        statements.append(
            "ALTER TABLE qr_code_assets ADD COLUMN hit_count INTEGER NOT NULL DEFAULT 0"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_db_session() -> Generator[Session, None, None]:
    """Her istek için yeni bir veritabanı oturumu açar."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
