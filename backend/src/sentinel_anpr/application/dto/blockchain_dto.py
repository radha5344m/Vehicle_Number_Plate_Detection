"""Blockchain evidence integrity DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportCommand


@dataclass(frozen=True)
class EvidenceBlockDto:
    """Persisted blockchain evidence block."""

    block_id: str
    block_number: int
    block_timestamp: datetime
    investigation_id: str
    report_id: str | None
    registration_number: str
    officer_id: str
    previous_hash: str
    current_hash: str
    report_sha256_hash: str


@dataclass(frozen=True)
class BlockchainEvidenceDto:
    """Blockchain evidence metadata returned with investigations."""

    block_number: int
    block_timestamp: datetime
    current_hash: str
    previous_hash: str
    report_sha256_hash: str
    integrity_verified: bool


@dataclass(frozen=True)
class AnchorEvidenceCommand:
    """Anchor a completed investigation report on the evidence chain."""

    investigation_id: str
    report_id: str
    registration_number: str
    officer_id: str
    report_command: GenerateInvestigationReportCommand


@dataclass(frozen=True)
class AnchorEvidenceResult:
    """Outcome of anchoring investigation evidence."""

    block: EvidenceBlockDto
    integrity_verified: bool = True


@dataclass(frozen=True)
class VerifyInvestigationIntegrityCommand:
    """Verify investigation report integrity against the evidence chain."""

    investigation_id: str
    report_command: GenerateInvestigationReportCommand


@dataclass(frozen=True)
class VerifyInvestigationIntegrityResult:
    """Integrity verification outcome."""

    investigation_id: str
    integrity_verified: bool
    report_sha256_hash: str
    stored_report_sha256_hash: str | None
    block: EvidenceBlockDto | None
    message: str
