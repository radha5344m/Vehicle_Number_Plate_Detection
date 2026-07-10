"""Hashing rules for evidence blockchain blocks."""

from __future__ import annotations

import hashlib
from datetime import datetime


GENESIS_PREVIOUS_HASH = "0" * 64


def compute_block_hash(
    *,
    block_number: int,
    block_timestamp: datetime,
    investigation_id: str,
    registration_number: str,
    officer_id: str,
    previous_hash: str,
    report_sha256_hash: str,
) -> str:
    """Compute the SHA-256 hash for a block payload."""
    timestamp = block_timestamp.isoformat()
    payload = (
        f"{block_number}|{timestamp}|{investigation_id}|{registration_number}|"
        f"{officer_id}|{previous_hash}|{report_sha256_hash}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
