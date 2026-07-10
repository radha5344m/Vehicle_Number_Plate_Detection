"""Compose dynamic investigation reasoning from existing investigation outputs.

This is presentation/report prose only — it does not recalculate risk, Vision,
or registry outcomes.
"""

from __future__ import annotations

from sentinel_anpr.application.dto.report_dto import GenerateInvestigationReportCommand


def compose_investigation_reasoning(command: GenerateInvestigationReportCommand) -> str:
    """Build narrative AI Reasoning from registration, Vision, registry, comparison, and risk."""
    paragraphs: list[str] = []

    vision = command.vision_analysis
    plate = (
        (vision.registration_number if vision and vision.registration_number else None)
        or (command.detected_plate or "")
    ).strip() or "UNKNOWN"
    confidence = command.ocr_result.ocr_confidence
    details = command.vehicle_details
    comparison = command.attribute_comparison
    lookup = (command.lookup_status or "").strip().lower()
    risk_level = (command.risk_level or "").strip().upper()
    risk_score_pct = int(round(max(0.0, min(1.0, command.risk_score)) * 100))

    vision_conf = vision.confidence if vision and vision.confidence is not None else confidence
    paragraphs.append(
        f"Vision AI extracted registration number {plate} with overall confidence "
        f"{vision_conf:.0%}."
    )
    if vision and vision.explanation and vision.explanation.strip():
        paragraphs.append(f"Vision model rationale: {vision.explanation.strip()}")

    if vision:
        observed_bits = [
            f"brand {vision.brand}" if vision.brand else None,
            f"model {vision.model}" if vision.model else None,
            f"color {vision.color}" if vision.color else None,
            f"type {vision.vehicle_type}" if vision.vehicle_type else None,
        ]
        observed = ", ".join(bit for bit in observed_bits if bit)
        if observed:
            paragraphs.append(f"Vision AI observed vehicle characteristics: {observed}.")

    if lookup in {"found", "matched", "match"}:
        owner = (details.registered_owner if details else None) or "the registered owner on file"
        status = (details.registration_status if details else None) or "recorded"
        paragraphs.append(
            f"Registry verification located a matching vehicle record for {plate}. "
            f"Registered owner is recorded as {owner}; registration status is {status}."
        )
    elif lookup in {"not_found", "missing", "absent"}:
        paragraphs.append(
            f"Registry verification did not locate an authoritative record for {plate}. "
            "Absence of a matching registry entry elevates investigative scrutiny."
        )
    elif command.verification_message:
        paragraphs.append(f"Registry verification outcome: {command.verification_message.strip()}")
    elif details and details.plate_number:
        paragraphs.append(
            f"Registry details were available for comparison against observed vehicle attributes "
            f"for plate {plate}."
        )
    else:
        paragraphs.append(
            f"No registry vehicle details were supplied for plate {plate} at report time."
        )

    if comparison and comparison.items:
        matched = [i for i in comparison.items if i.matches is True]
        mismatched = [i for i in comparison.items if i.matches is False]
        unknown = [i for i in comparison.items if i.matches is None]
        match_pct = int(round((len(matched) / len(comparison.items)) * 100)) if comparison.items else 0
        paragraphs.append(
            f"Attribute comparison against the registry covered {len(comparison.items)} "
            f"observable fields with an overall match rate of {match_pct}% "
            f"({len(matched)} match, {len(mismatched)} mismatch, {len(unknown)} inconclusive)."
        )
        if mismatched:
            parts = []
            for item in mismatched:
                observed = item.observed or "—"
                registered = item.registered or "—"
                parts.append(
                    f"{item.attribute}: vision '{observed}' vs registered '{registered}'"
                )
            paragraphs.append("Material mismatches: " + "; ".join(parts) + ".")
        if comparison.overall_match is True:
            paragraphs.append(
                "Overall attribute profile is consistent with the registered vehicle identity."
            )
        elif comparison.overall_match is False:
            paragraphs.append(
                "Overall attribute profile is inconsistent with the registered vehicle identity, "
                "which may indicate cloning, misread attributes, or registry drift."
            )

    paragraphs.append(
        f"The risk engine assigned level {risk_level} with score {risk_score_pct}/100."
    )
    if command.risk_explanation and command.risk_explanation.strip():
        paragraphs.append(f"Risk explanation: {command.risk_explanation.strip()}")
    if command.risk_signals:
        signal_bits = [
            f"{signal.name} (weight {signal.weight:.2f}): {signal.detail}"
            for signal in command.risk_signals
        ]
        paragraphs.append("Contributing risk signals — " + "; ".join(signal_bits) + ".")

    if command.investigation_summary and command.investigation_summary.strip():
        paragraphs.append(f"Investigation summary: {command.investigation_summary.strip()}")

    paragraphs.append(
        f"Officer recommendation from the risk assessment policy: {command.recommendation.strip()}"
    )

    return " ".join(paragraphs)
