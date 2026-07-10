"""Attribute comparison policy unit tests."""

from sentinel_anpr.domain.verification.services.attribute_comparison_policy import (
    AttributeComparisonPolicy,
)


def test_compare_matches_registry_attributes() -> None:
    policy = AttributeComparisonPolicy()
    result = policy.compare(
        observed_color="white",
        observed_vehicle_type="car",
        observed_brand="Toyota",
        color_confidence=0.9,
        vehicle_type_confidence=0.85,
        brand_confidence=0.7,
        registered_color="White",
        registered_vehicle_type="car",
        registered_make="Toyota",
    )
    assert result.overall_match is True
    assert all(item.matches is True for item in result.items if item.matches is not None)


def test_compare_detects_color_mismatch() -> None:
    policy = AttributeComparisonPolicy()
    result = policy.compare(
        observed_color="black",
        observed_vehicle_type="car",
        observed_brand="Toyota",
        color_confidence=0.9,
        vehicle_type_confidence=0.85,
        brand_confidence=0.7,
        registered_color="white",
        registered_vehicle_type="car",
        registered_make="Toyota",
    )
    color_item = next(item for item in result.items if item.attribute == "color")
    assert color_item.matches is False
    assert result.overall_match is False


def test_compare_without_registry_returns_empty() -> None:
    policy = AttributeComparisonPolicy()
    result = policy.compare(
        observed_color="white",
        observed_vehicle_type="car",
        observed_brand="Toyota",
        color_confidence=0.9,
        vehicle_type_confidence=0.85,
        brand_confidence=0.7,
        registered_color=None,
        registered_vehicle_type=None,
        registered_make=None,
    )
    assert result.items == ()
    assert result.overall_match is None
