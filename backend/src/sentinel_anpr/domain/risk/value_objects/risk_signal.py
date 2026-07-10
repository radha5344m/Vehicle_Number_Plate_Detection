"""Explainable risk signal."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskSignal:
    """Named contributor to the composite risk score."""

    name: str
    weight: float
    detail: str
