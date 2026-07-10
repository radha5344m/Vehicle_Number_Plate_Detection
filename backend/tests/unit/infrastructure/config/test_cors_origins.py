"""Tests for CORS origin parsing."""

from sentinel_anpr.infrastructure.config.settings import (
    Settings,
    parse_cors_origins,
    resolve_cors_origins,
)


def test_parse_cors_origins_splits_and_trims() -> None:
    assert parse_cors_origins(
        "http://localhost:5173, https://sentinel.onrender.com ,"
    ) == [
        "http://localhost:5173",
        "https://sentinel.onrender.com",
    ]


def test_parse_cors_origins_empty() -> None:
    assert parse_cors_origins(None) == []
    assert parse_cors_origins("") == []


def test_resolve_cors_origins_merges_frontend_url() -> None:
    settings = Settings(
        cors_origins="http://localhost:5173",
        frontend_url="https://vehicle-number-plate-detection-rho.vercel.app",
    )
    assert resolve_cors_origins(settings) == [
        "http://localhost:5173",
        "https://vehicle-number-plate-detection-rho.vercel.app",
    ]
