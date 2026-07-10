"""Vehicle image upload response schema."""

from datetime import datetime

from pydantic import BaseModel


class UploadImageResponseData(BaseModel):
    """Stored vehicle image metadata."""

    upload_id: str
    storage_key: str
    original_filename: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    uploaded_at: datetime
