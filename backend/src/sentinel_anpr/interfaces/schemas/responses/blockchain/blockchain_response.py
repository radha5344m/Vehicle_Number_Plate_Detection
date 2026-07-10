"""Blockchain evidence integrity API schemas."""

from datetime import datetime

from pydantic import BaseModel


class BlockchainEvidenceData(BaseModel):
    """Blockchain evidence metadata attached to investigations."""

    block_number: int
    block_timestamp: datetime
    current_hash: str
    previous_hash: str
    report_sha256_hash: str
    integrity_verified: bool


class BlockchainIntegrityVerificationData(BaseModel):
    """Integrity verification response."""

    investigation_id: str
    integrity_verified: bool
    report_sha256_hash: str
    stored_report_sha256_hash: str | None
    block_number: int | None
    current_hash: str | None
    block_timestamp: datetime | None
    message: str
