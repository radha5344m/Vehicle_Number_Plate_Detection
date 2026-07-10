"""Local filesystem image storage adapter."""

import uuid
from pathlib import Path

from sentinel_anpr.application.ports.outbound.image_storage_port import ImageStoragePort, StoredImageRef


class LocalImageStorage(ImageStoragePort):
    """Persist vehicle images to a local directory."""

    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)

    def store(
        self,
        *,
        officer_id: str,
        content: bytes,
        content_type: str,
        original_filename: str,
        width: int,
        height: int,
    ) -> StoredImageRef:
        upload_id = str(uuid.uuid4())
        extension = ".jpg" if content_type == "image/jpeg" else ".png"
        relative_key = f"{officer_id}/{upload_id}{extension}"
        destination = self._base_dir / relative_key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

        return StoredImageRef(
            upload_id=upload_id,
            storage_key=relative_key.replace("\\", "/"),
            content_type=content_type,
            size_bytes=len(content),
            width=width,
            height=height,
        )
