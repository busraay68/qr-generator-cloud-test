"""Depolama servisi."""

from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from src.config import Settings


@dataclass
class DownloadedObject:
    """İndirilen nesnenin içeriğini taşır."""

    body: bytes
    content_type: str
    size_bytes: int


class StorageService:
    """S3 ve yerel depolama işlemlerini yönetir."""

    def __init__(
        self,
        bucket_name: str,
        region_name: str,
        endpoint_url: str | None,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_session_token: str | None = None,
        local_storage_dir: Path | None = None,
    ) -> None:
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.backend = "s3"
        self.local_storage_dir = (local_storage_dir or Path("./local_storage")).resolve()
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)
        self.client = boto3.client(
            "s3",
            region_name=region_name,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            config=Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 0}),
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> "StorageService":
        """Ayar nesnesinden depolama servisi üretir."""

        return cls(
            bucket_name=settings.s3_bucket_name,
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            aws_session_token=settings.aws_session_token,
            local_storage_dir=settings.local_storage_dir,
        )

    def _local_path(self, object_key: str) -> Path:
        """Nesne anahtarını yerel dosya yoluna çevirir."""

        return self.local_storage_dir / object_key

    def _switch_to_local(self) -> None:
        """Depolama katmanını yerel moda geçirir."""

        self.backend = "local"

    def ensure_bucket(self) -> None:
        """Bucket erişimini doğrular, gerekirse oluşturur."""

        if self.backend == "local":
            return
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return
        except (BotoCoreError, ClientError):
            create_kwargs = {"Bucket": self.bucket_name}
            try:
                if self.region_name != "us-east-1":
                    create_kwargs["CreateBucketConfiguration"] = {
                        "LocationConstraint": self.region_name,
                    }
                self.client.create_bucket(**create_kwargs)
            except (BotoCoreError, ClientError):
                self._switch_to_local()

    def upload_object(self, object_key: str, payload: bytes, content_type: str) -> None:
        """Nesneyi depolamaya yazar."""

        if self.backend == "local":
            local_path = self._local_path(object_key)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(payload)
            return

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=payload,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError):
            self._switch_to_local()
            local_path = self._local_path(object_key)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(payload)

    def download(self, object_key: str) -> DownloadedObject:
        """Nesneyi depolamadan okur."""

        if self.backend == "local":
            local_path = self._local_path(object_key)
            body = local_path.read_bytes()
            content_type = "image/svg+xml" if local_path.suffix == ".svg" else "image/png"
            return DownloadedObject(body=body, content_type=content_type, size_bytes=len(body))

        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
            body = response["Body"].read()
            return DownloadedObject(
                body=body,
                content_type=response.get("ContentType", "image/png"),
                size_bytes=len(body),
            )
        except (BotoCoreError, ClientError):
            self._switch_to_local()
            local_path = self._local_path(object_key)
            body = local_path.read_bytes()
            content_type = "image/svg+xml" if local_path.suffix == ".svg" else "image/png"
            return DownloadedObject(body=body, content_type=content_type, size_bytes=len(body))

    def delete(self, object_key: str) -> None:
        """Nesneyi depolamadan siler."""

        if self.backend == "local":
            self._local_path(object_key).unlink(missing_ok=True)
            return

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
        except (BotoCoreError, ClientError):
            self._switch_to_local()
            self._local_path(object_key).unlink(missing_ok=True)
