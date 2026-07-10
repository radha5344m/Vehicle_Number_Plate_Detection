"""Compare observed vehicle attributes against registry records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AttributeComparisonItem:
    """Single attribute comparison outcome."""

    attribute: str
    observed: str
    registered: str | None
    matches: bool | None
    confidence: float | None


@dataclass(frozen=True)
class AttributeComparisonResult:
    """Structured attribute comparison for investigation reporting."""

    items: tuple[AttributeComparisonItem, ...]
    overall_match: bool | None


class AttributeComparisonPolicy:
    """Compare OCR-derived visual attributes with registry vehicle data."""

    def compare(
        self,
        *,
        observed_color: str,
        observed_vehicle_type: str,
        observed_brand: str | None,
        color_confidence: float,
        vehicle_type_confidence: float,
        brand_confidence: float | None,
        registered_color: str | None,
        registered_vehicle_type: str | None,
        registered_make: str | None,
    ) -> AttributeComparisonResult:
        if registered_color is None and registered_vehicle_type is None:
            return AttributeComparisonResult(items=(), overall_match=None)

        items = (
            AttributeComparisonItem(
                attribute="color",
                observed=observed_color,
                registered=registered_color,
                matches=_colors_match(observed_color, registered_color)
                if registered_color
                else None,
                confidence=color_confidence,
            ),
            AttributeComparisonItem(
                attribute="vehicle_type",
                observed=observed_vehicle_type,
                registered=registered_vehicle_type,
                matches=_types_match(observed_vehicle_type, registered_vehicle_type)
                if registered_vehicle_type
                else None,
                confidence=vehicle_type_confidence,
            ),
            AttributeComparisonItem(
                attribute="brand",
                observed=observed_brand or "Not detected",
                registered=registered_make,
                matches=_brands_match(observed_brand, registered_make)
                if observed_brand and registered_make
                else None,
                confidence=brand_confidence,
            ),
        )
        comparable = [item for item in items if item.matches is not None]
        overall_match = all(item.matches for item in comparable) if comparable else None
        return AttributeComparisonResult(items=items, overall_match=overall_match)


def _normalize_token(value: str) -> str:
    return value.strip().lower()


def _colors_match(observed: str, registered: str) -> bool:
    return _normalize_token(observed) == _normalize_token(registered)


def _types_match(observed: str, registered: str) -> bool:
    observed_type = _normalize_token(observed)
    registered_type = _normalize_token(registered)
    if observed_type == registered_type:
        return True
    compatible_groups = (
        {"car", "suv"},
        {"truck", "bus"},
    )
    return any(
        observed_type in group and registered_type in group for group in compatible_groups
    )


def _brands_match(observed_brand: str, registered_make: str) -> bool:
    observed = _normalize_token(observed_brand)
    registered = _normalize_token(registered_make)
    return observed in registered or registered in observed
