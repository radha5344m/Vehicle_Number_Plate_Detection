"""Vehicle image upload data transfer objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UploadImageCommand:
    """Incoming vehicle image upload."""

    officer_id: str
    content: bytes
    content_type: str
    original_filename: str


@dataclass(frozen=True)
class UploadImageResult:
    """Stored vehicle image metadata."""

    upload_id: str
    storage_key: str
    original_filename: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    uploaded_at: datetime
