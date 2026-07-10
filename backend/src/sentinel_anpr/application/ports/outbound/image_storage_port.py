"""Vehicle image storage port."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StoredImageRef:
    """Reference to a persisted image."""

    upload_id: str
    storage_key: str
    content_type: str
    size_bytes: int
    width: int
    height: int


class ImageStoragePort(Protocol):
    """Store vehicle images without processing them."""

    def store(
        self,
        *,
        officer_id: str,
        content: bytes,
        content_type: str,
        original_filename: str,
        width: int,
        height: int,
    ) -> StoredImageRef: ...
