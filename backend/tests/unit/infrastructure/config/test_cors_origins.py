"""Tests for CORS origin parsing."""

from sentinel_anpr.infrastructure.config.settings import parse_cors_origins


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
