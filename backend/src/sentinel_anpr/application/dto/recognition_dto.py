"""Registration-number recognition data transfer objects.

Carries the recognised registration number (produced by the vision AI service)
into the verification and risk-assessment use cases.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RecognizePlateResult:
    """Recognised registration number and its confidence metadata."""

    registration_number: str
    detected_plate_text: str
    ocr_confidence: float
    char_confidences: tuple[float, ...]
    model_version: str
