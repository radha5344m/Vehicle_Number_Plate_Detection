"""Environment-backed application settings."""

from functools import lru_cache
import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve backend/.env regardless of process working directory.
_BACKEND_DIR = Path(__file__).resolve().parents[4]
_ENV_FILE = _BACKEND_DIR / ".env"


def get_backend_dir() -> Path:
    """Absolute path to the backend project root."""
    return _BACKEND_DIR


def get_env_file_path() -> Path:
    """Absolute path to the backend .env file."""
    return _ENV_FILE


def _running_under_pytest() -> bool:
    """True while a pytest test function is executing."""
    return os.getenv("PYTEST_CURRENT_TEST") is not None


def load_env_file() -> Path:
    """Load backend/.env into os.environ.

    When not running under pytest, values from ``backend/.env`` override stale
    process-level variables (e.g. ``SENTINEL_VISION_PROVIDER=stub`` left in a
    shell session). During pytest, process env is preserved so the autouse stub
    fixture continues to work.
    """
    if _ENV_FILE.is_file():
        load_dotenv(_ENV_FILE, override=not _running_under_pytest())
    return _ENV_FILE


def resolve_gemini_api_key(settings: "Settings | None" = None) -> str | None:
    """Resolve the Gemini API key from backend/.env, Settings, then process env."""
    if settings is None:
        settings = get_settings()

    candidates: list[str | None] = []
    if _ENV_FILE.is_file():
        candidates.append(dotenv_values(_ENV_FILE).get("GEMINI_API_KEY"))
    candidates.extend([settings.gemini_api_key, os.getenv("GEMINI_API_KEY")])

    for candidate in candidates:
        if candidate is None:
            continue
        normalized = str(candidate).strip().strip('"').strip("'")
        if normalized:
            return normalized
    return None


def gemini_api_key_length(settings: "Settings | None" = None) -> int:
    """Return Gemini API key length for startup diagnostics (never expose the key)."""
    key = resolve_gemini_api_key(settings)
    return len(key) if key else 0


def gemini_api_key_exists(settings: "Settings | None" = None) -> bool:
    """Return True when a non-empty Gemini API key is configured."""
    return bool(resolve_gemini_api_key(settings))


class MissingGeminiApiKeyError(RuntimeError):
    """Raised at startup when Gemini is selected but GEMINI_API_KEY is missing."""


def validate_vision_configuration(settings: "Settings | None" = None) -> None:
    """Validate vision provider configuration at application startup.

    When ``SENTINEL_VISION_PROVIDER=gemini``, ``GEMINI_API_KEY`` is required.
    ``OPENAI_API_KEY`` is never read or validated for any provider.
    """
    if settings is None:
        settings = get_settings()

    provider = (settings.vision_provider or "gemini").strip().lower()
    if provider != "gemini":
        return

    if gemini_api_key_exists(settings):
        return

    raise MissingGeminiApiKeyError(
        "GEMINI_API_KEY is not set. "
        "When SENTINEL_VISION_PROVIDER=gemini, create backend/.env from .env.example "
        "and set GEMINI_API_KEY (Google AI Studio / Gemini API key). "
        "Optional: SENTINEL_GEMINI_MODEL (default gemini-2.5-flash). "
        "For local development without Gemini, set SENTINEL_VISION_PROVIDER=stub."
    )


class Settings(BaseSettings):
    """Load configuration from environment variables and optional .env file."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        env_prefix="SENTINEL_",
        extra="ignore",
        populate_by_name=True,
    )

    env: str = Field(default="development", alias="ENV")
    app_name: str = Field(default="sentinel-anpr-ai")
    log_level: str = Field(default="INFO")
    database_url: str = Field(default="sqlite:///./data/sentinel_anpr.db")
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8080)
    auth_jwt_secret: str = Field(default="dev-only-change-in-production")
    auth_jwt_issuer: str = Field(default="sentinel-anpr-ai")
    auth_access_token_ttl_seconds: int = Field(default=900)
    auth_refresh_token_ttl_seconds: int = Field(default=604800)
    upload_storage_dir: str = Field(default="data/uploads")
    report_storage_dir: str = Field(default="data/reports")

    # Vision provider: "gemini" (Google Gemini Vision) or "stub" (tests/local).
    vision_provider: str = Field(default="gemini")
    # GEMINI_API_KEY (no SENTINEL_ prefix) via AliasChoices; also accepts SENTINEL_GEMINI_API_KEY.
    gemini_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "SENTINEL_GEMINI_API_KEY"),
    )
    # Bound from SENTINEL_GEMINI_MODEL (default gemini-2.5-flash).
    gemini_model: str = Field(default="gemini-2.5-flash")


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    load_env_file()
    return Settings()


def reload_settings() -> Settings:
    """Drop cached settings and reload from environment / .env."""
    get_settings.cache_clear()
    return get_settings()
