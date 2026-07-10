"""Generate human-readable investigation summaries from vision AI observations only."""

from __future__ import annotations

from dataclasses import dataclass

_CONFIDENCE_THRESHOLD = 0.60
_UNKNOWN_TOKENS = frozenset(
    {"", "unknown", "n/a", "na", "none", "not detected", "not clearly visible"}
)


@dataclass(frozen=True)
class InvestigationSummaryInput:
    """Vision-only facts required to compose an investigation narrative."""

    plate_detected: bool
    registration_number: str | None
    registration_confidence: float | None
    vehicle_category: str | None
    vehicle_category_confidence: float | None
    brand: str | None
    brand_confidence: float | None
    model: str | None
    model_confidence: float | None
    color: str | None
    color_confidence: float | None
    overall_confidence: float | None
    vision_explanation: str | None


class InvestigationSummaryPolicy:
    """Build an investigation narrative from vision AI observations only."""

    def build(self, inputs: InvestigationSummaryInput) -> str:
        if not inputs.plate_detected:
            return (
                "Vision AI could not detect a readable number plate in the uploaded image. "
                "Vehicle attributes cannot be determined from the available image."
            )

        parts: list[str] = [
            self._opening_observation(inputs),
            self._registration_statement(inputs),
            self._brand_model_statement(inputs),
            self._color_statement(inputs),
        ]

        if inputs.overall_confidence is not None:
            parts.append(f"Overall vision confidence: {inputs.overall_confidence:.0%}.")

        if inputs.vision_explanation and inputs.vision_explanation.strip():
            explanation = inputs.vision_explanation.strip()
            if not explanation.endswith("."):
                explanation = f"{explanation}."
            parts.append(explanation)

        return " ".join(part for part in parts if part)

    def _opening_observation(self, inputs: InvestigationSummaryInput) -> str:
        color_confident = _is_confident(inputs.color, inputs.color_confidence)
        category_confident = _is_confident(
            inputs.vehicle_category,
            inputs.vehicle_category_confidence,
        )

        if color_confident and category_confident:
            return (
                f"Vision AI observed a {inputs.color.strip()} coloured "
                f"{inputs.vehicle_category.strip()}."
            )
        if category_confident:
            return f"Vision AI observed a {inputs.vehicle_category.strip()}."
        if color_confident:
            return f"Vision AI observed a {inputs.color.strip()} coloured vehicle."
        return "Vision AI analyzed the uploaded vehicle image."

    def _registration_statement(self, inputs: InvestigationSummaryInput) -> str:
        registration = (inputs.registration_number or "").strip()
        if not registration or _is_unknown(registration):
            return "Registration number: not clearly visible in the image."

        if _is_confident(registration, inputs.registration_confidence):
            return f"Registration number: {registration} (readable from the plate)."

        if (
            inputs.registration_confidence is not None
            and inputs.registration_confidence < _CONFIDENCE_THRESHOLD
        ):
            return (
                "The registration plate appears partially readable; the full number "
                "cannot be determined with sufficient confidence from the available image."
            )

        return (
            f"Registration plate text appears as {registration}, but legibility is uncertain."
        )

    def _brand_model_statement(self, inputs: InvestigationSummaryInput) -> str:
        brand_confident = _is_confident(inputs.brand, inputs.brand_confidence)
        model_confident = _is_confident(inputs.model, inputs.model_confidence)

        if brand_confident and model_confident:
            return (
                f"Manufacturer: {inputs.brand.strip()}. "
                f"Model: {inputs.model.strip()}."
            )
        if brand_confident:
            return (
                f"Manufacturer: {inputs.brand.strip()}. "
                "Model: cannot be determined from the image."
            )
        if model_confident:
            return (
                f"Model: {inputs.model.strip()}. "
                "Manufacturer: cannot be determined from the image."
            )
        return (
            "Manufacturer and exact model cannot be determined with sufficient confidence "
            "from the available image."
        )

    def _color_statement(self, inputs: InvestigationSummaryInput) -> str:
        if _is_confident(inputs.color, inputs.color_confidence):
            return f"Primary colour: {inputs.color.strip()}."
        if inputs.color and not _is_unknown(inputs.color):
            return "Primary colour: not clearly visible in the image."
        return "Primary colour: cannot be determined from the image."


def _is_unknown(value: str) -> bool:
    return value.strip().lower() in _UNKNOWN_TOKENS


def _is_confident(value: str | None, confidence: float | None) -> bool:
    if not value or _is_unknown(value):
        return False
    if confidence is None:
        return True
    return confidence >= _CONFIDENCE_THRESHOLD
