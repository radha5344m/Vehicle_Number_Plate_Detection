"""Report file integrity helpers."""

import hashlib


def checksum_pdf(pdf_bytes: bytes) -> str:
    """Compute SHA-256 checksum for a PDF payload."""
    return hashlib.sha256(pdf_bytes).hexdigest()
