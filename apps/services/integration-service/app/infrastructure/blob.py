from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO


@dataclass(frozen=True)
class Blob:
    uri: str
    content_type: str
    data: bytes


class BlobLandingAdapter(ABC):
    @abstractmethod
    def land(self, source_id: str, data: bytes, content_type: str) -> Blob: ...

    @abstractmethod
    def read(self, uri: str) -> bytes: ...


class InMemoryBlobLandingAdapter(BlobLandingAdapter):
    def __init__(self, prefix: str = "memory://landing") -> None:
        self.prefix = prefix.rstrip("/")
        self._objects: dict[str, bytes] = {}

    def land(self, source_id: str, data: bytes, content_type: str) -> Blob:
        digest = sha256(data).hexdigest()
        uri = f"{self.prefix}/{source_id}/{digest}"
        self._objects[uri] = data
        return Blob(uri=uri, content_type=content_type, data=data)

    def read(self, uri: str) -> bytes:
        try:
            return self._objects[uri]
        except KeyError as exc:
            raise FileNotFoundError(uri) from exc


class AzureBlobLandingAdapter(BlobLandingAdapter):
    """Immutable raw landing adapter backed by Azure Blob Storage."""

    def __init__(self, connection_string: str, container: str) -> None:
        from azure.storage.blob import BlobServiceClient, ContentSettings

        self.container = container
        self.content_settings = ContentSettings
        self.client = BlobServiceClient.from_connection_string(connection_string)
        self.client.create_container(container)

    def land(self, source_id: str, data: bytes, content_type: str) -> Blob:
        digest = sha256(data).hexdigest()
        name = f"raw/{source_id}/{digest}"
        blob = self.client.get_blob_client(self.container, name)
        blob.upload_blob(
            BytesIO(data),
            overwrite=False,
            content_settings=self.content_settings(content_type=content_type),
        )
        return Blob(
            uri=f"azure://{self.container}/{name}",
            content_type=content_type,
            data=data,
        )

    def read(self, uri: str) -> bytes:
        prefix = f"azure://{self.container}/"
        if not uri.startswith(prefix):
            raise ValueError("URI does not belong to the configured landing container")
        name = uri[len(prefix):]
        return self.client.get_blob_client(self.container, name).download_blob().readall()
