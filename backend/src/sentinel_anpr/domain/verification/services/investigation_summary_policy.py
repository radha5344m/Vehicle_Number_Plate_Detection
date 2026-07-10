"""Generate human-readable investigation summaries for officers."""

from __future__ import annotations

from dataclasses import dataclass

from sentinel_anpr.domain.verification.services.attribute_comparison_policy import (
    AttributeComparisonResult,
)


@dataclass(frozen=True)
class InvestigationSummaryInput:
    """Facts required to compose an investigation narrative."""

    plate_detected: bool
    detection_confidence: float | None
    registration_number: str | None
    ocr_confidence: float | None
    vehicle_found: bool
    registration_status: str | None
    attribute_comparison: AttributeComparisonResult | None
    risk_level: str | None


class InvestigationSummaryPolicy:
    """Build a police-grade investigation narrative from workflow facts."""

    def build(self, inputs: InvestigationSummaryInput) -> str:
        if not inputs.plate_detected:
            return "No number plate was detected in the uploaded image."

        lines: list[str] = ["Plate detected successfully."]

        if inputs.registration_number:
            lines.append(f"Registration {inputs.registration_number} read from the plate.")
        if inputs.ocr_confidence is not None:
            lines.append(f"OCR confidence is {inputs.ocr_confidence:.0%}.")

        if not inputs.vehicle_found:
            lines.append("Vehicle was not found in the registry.")
            lines.append("Possible fake plate or unregistered vehicle.")
            return " ".join(lines)

        lines.append("Registration found in the vehicle registry.")

        if inputs.registration_status:
            status = inputs.registration_status.strip().lower()
            if status == "stolen":
                lines.append("Vehicle is flagged as stolen in the registry.")
            elif status == "suspended":
                lines.append("Vehicle registration is suspended.")
            elif status == "active":
                lines.append("Registration status is active.")

        comparison = inputs.attribute_comparison
        if comparison and comparison.items:
            for item in comparison.items:
                if item.matches is True:
                    lines.append(f"Observed {item.attribute.replace('_', ' ')} matches registry.")
                elif item.matches is False:
                    lines.append(
                        f"Observed {item.attribute.replace('_', ' ')} "
                        f"({item.observed}) does not match registry "
                        f"({item.registered})."
                    )

        if inputs.risk_level:
            lines.append(f"Overall risk is {inputs.risk_level.upper()}.")

        return " ".join(lines)
