"""Investigation report response schemas."""

from datetime import datetime

from pydantic import BaseModel


class InvestigationReportResponseData(BaseModel):
    """Generated report metadata."""

    report_id: str
    title: str
    file_size_bytes: int
    checksum_sha256: str
    generated_at: datetime
    download_url: str
