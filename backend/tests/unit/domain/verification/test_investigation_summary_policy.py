"""Investigation summary policy unit tests."""

from sentinel_anpr.domain.verification.services.investigation_summary_policy import (
    InvestigationSummaryInput,
    InvestigationSummaryPolicy,
)


def test_summary_describes_confident_vision_attributes_only() -> None:
    policy = InvestigationSummaryPolicy()
    summary = policy.build(
        InvestigationSummaryInput(
            plate_detected=True,
            registration_number="AP09AB1234",
            registration_confidence=0.9,
            vehicle_category="car",
            vehicle_category_confidence=0.9,
            brand="Toyota",
            brand_confidence=0.88,
            model="Innova",
            model_confidence=0.86,
            color="white",
            color_confidence=0.9,
            overall_confidence=0.9,
            vision_explanation="Clear front plate and unobstructed body panels.",
        )
    )
    assert "Vision AI observed a white coloured car." in summary
    assert "AP09AB1234" in summary
    assert "Manufacturer: Toyota." in summary
    assert "Model: Innova." in summary
    assert "Primary colour: white." in summary
    assert "Overall vision confidence: 90%." in summary
    assert "Clear front plate" in summary
    assert "registry" not in summary.lower()
    assert "risk" not in summary.lower()


def test_summary_never_mentions_registry_even_when_provided_in_other_layers() -> None:
    policy = InvestigationSummaryPolicy()
    summary = policy.build(
        InvestigationSummaryInput(
            plate_detected=True,
            registration_number="AP09AB1234",
            registration_confidence=0.91,
            vehicle_category="car",
            vehicle_category_confidence=0.91,
            brand="Honda",
            brand_confidence=0.85,
            model="City",
            model_confidence=0.84,
            color="black",
            color_confidence=0.9,
            overall_confidence=0.91,
            vision_explanation="Observed in daylight with partial side angle.",
        )
    )
    assert "black coloured car" in summary
    assert "Honda" in summary
    assert "white" not in summary
    assert "Toyota" not in summary
    assert "registry" not in summary.lower()
    assert "mismatch" not in summary.lower()


def test_summary_marks_low_confidence_attributes_as_undetermined() -> None:
    policy = InvestigationSummaryPolicy()
    summary = policy.build(
        InvestigationSummaryInput(
            plate_detected=True,
            registration_number="AP09AB1234",
            registration_confidence=0.45,
            vehicle_category="two-wheeler",
            vehicle_category_confidence=0.82,
            brand=None,
            brand_confidence=None,
            model=None,
            model_confidence=None,
            color="dark",
            color_confidence=0.55,
            overall_confidence=0.55,
            vision_explanation=(
                "Parked near a building; manufacturer markings are not clearly visible."
            ),
        )
    )
    assert "two-wheeler" in summary
    assert "partially readable" in summary
    assert "Manufacturer and exact model cannot be determined" in summary
    assert "Primary colour: not clearly visible" in summary
    assert "Parked near a building" in summary


def test_summary_when_no_plate_detected() -> None:
    policy = InvestigationSummaryPolicy()
    summary = policy.build(
        InvestigationSummaryInput(
            plate_detected=False,
            registration_number=None,
            registration_confidence=None,
            vehicle_category=None,
            vehicle_category_confidence=None,
            brand=None,
            brand_confidence=None,
            model=None,
            model_confidence=None,
            color=None,
            color_confidence=None,
            overall_confidence=None,
            vision_explanation=None,
        )
    )
    assert "could not detect a readable number plate" in summary
