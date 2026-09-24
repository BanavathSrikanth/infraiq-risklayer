from pathlib import Path

from app.config import Settings


class SourceFileClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def read(self, source_uri: str) -> tuple[str, bytes]:
        if source_uri.startswith("file://"):
            path = Path(source_uri.removeprefix("file://"))
            return path.name, path.read_bytes()
        if source_uri.startswith("https://"):
            from azure.storage.blob import BlobClient

            client = BlobClient.from_blob_url(source_uri)
            return Path(client.blob_name).name, client.download_blob().readall()
        if source_uri.startswith("blob://"):
            if not self.settings.blob_connection_string:
                raise ValueError("BLOB_CONNECTION_STRING is required for blob:// sources")
            from azure.storage.blob import BlobClient

            container, blob_name = source_uri.removeprefix("blob://").split("/", 1)
            client = BlobClient.from_connection_string(
                self.settings.blob_connection_string, container_name=container, blob_name=blob_name
            )
            return Path(blob_name).name, client.download_blob().readall()
        path = Path(source_uri)
        return path.name, path.read_bytes()