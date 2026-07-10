"""Plate text normalization helpers."""

import re


def normalize_registration_number(raw_text: str) -> str:
    """Normalize OCR output to an uppercase alphanumeric registration number."""
    return re.sub(r"[^A-Z0-9]", "", raw_text.upper())
