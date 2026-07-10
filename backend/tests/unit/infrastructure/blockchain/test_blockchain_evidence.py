"""Blockchain evidence integrity tests."""

import json
from dataclasses import replace
from datetime import UTC, datetime

from sentinel_anpr.application.dto.report_dto import (
    GenerateInvestigationReportCommand,
    OcrResultDto,
)
from sentinel_anpr.domain.blockchain.services.evidence_block_hash_policy import compute_block_hash
from sentinel_anpr.infrastructure.blockchain.report_json_hasher import hash_investigation_report_json


def _sample_command() -> GenerateInvestigationReportCommand:
    return GenerateInvestigationReportCommand(
        officer_id="officer-1",
        officer_name="Test Officer",
        badge_number="AP001",
        officer_rank="Constable",
        vehicle_image_bytes=b"vehicle-image-bytes",
        detected_plate="AP09AB1234",
        ocr_result=OcrResultDto(
            registration_number="AP09AB1234",
            detected_plate_text="AP09AB1234",
            ocr_confidence=0.91,
        ),
        vehicle_details=None,
        risk_score=0.2,
        risk_level="low",
        recommendation="Routine check",
        workflow_id="workflow-1",
        scan_id="scan-1",
    )


def test_report_json_hash_is_deterministic() -> None:
    command = _sample_command()
    first = hash_investigation_report_json(command)
    second = hash_investigation_report_json(command)
    assert first == second
    assert len(first) == 64


def test_report_json_hash_changes_when_report_changes() -> None:
    command = _sample_command()
    modified = replace(command, recommendation="Escalate immediately")
    assert hash_investigation_report_json(command) != hash_investigation_report_json(modified)


def test_block_hash_links_previous_hash() -> None:
    now = datetime.now(UTC)
    report_hash = hash_investigation_report_json(_sample_command())
    previous_hash = "0" * 64
    current_hash = compute_block_hash(
        block_number=1,
        block_timestamp=now,
        investigation_id="scan-1",
        registration_number="AP09AB1234",
        officer_id="officer-1",
        previous_hash=previous_hash,
        report_sha256_hash=report_hash,
    )
    assert current_hash != previous_hash
    assert len(current_hash) == 64
