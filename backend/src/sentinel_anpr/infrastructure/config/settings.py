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
_DEFAULT_HF_MODEL = "google/gemma-3-4b-it:deepinfra"
_DEFAULT_HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
_DEFAULT_SARVAM_API_URL = "https://api.sarvam.ai/v1/chat/completions"
_DEFAULT_SARVAM_MODEL = "sarvam-30b"


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


def resolve_hf_token(settings: "Settings | None" = None) -> str | None:
    """Resolve the Hugging Face token from backend/.env, Settings, then process env."""
    if settings is None:
        settings = get_settings()

    candidates: list[str | None] = []
    if _ENV_FILE.is_file():
        candidates.append(dotenv_values(_ENV_FILE).get("HF_TOKEN"))
    candidates.extend([settings.hf_token, os.getenv("HF_TOKEN")])

    for candidate in candidates:
        if candidate is None:
            continue
        normalized = str(candidate).strip().strip('"').strip("'")
        if normalized:
            return normalized
    return None


def hf_token_exists(settings: "Settings | None" = None) -> bool:
    """Return True when a non-empty Hugging Face token is configured."""
    return bool(resolve_hf_token(settings))


def resolve_sarvam_api_key(settings: "Settings | None" = None) -> str | None:
    """Resolve the Sarvam API key from backend/.env, Settings, then process env."""
    if settings is None:
        settings = get_settings()

    candidates: list[str | None] = []
    if _ENV_FILE.is_file():
        candidates.append(dotenv_values(_ENV_FILE).get("SARVAM_API_KEY"))
    candidates.extend([settings.sarvam_api_key, os.getenv("SARVAM_API_KEY")])

    for candidate in candidates:
        if candidate is None:
            continue
        normalized = str(candidate).strip().strip('"').strip("'")
        if normalized:
            return normalized
    return None


def resolve_hf_api_url(
    *,
    model: str | None = None,
    api_url: str | None = None,
    settings: "Settings | None" = None,
) -> str:
    """Resolve the Hugging Face inference endpoint URL."""
    if settings is None:
        settings = get_settings()

    configured = (api_url or settings.hf_api_url or "").strip()
    resolved_model = (model or settings.hf_model or _DEFAULT_HF_MODEL).strip() or _DEFAULT_HF_MODEL

    if configured:
        if "{model}" in configured:
            return configured.replace("{model}", resolved_model)
        return configured

    return _DEFAULT_HF_API_URL


class MissingHuggingFaceTokenError(RuntimeError):
    """Raised at startup when Hugging Face is selected but HF_TOKEN is missing."""


def validate_vision_configuration(settings: "Settings | None" = None) -> None:
    """Validate vision provider configuration at application startup.

    When ``SENTINEL_VISION_PROVIDER=huggingface``, ``HF_TOKEN`` is required.
    """
    if settings is None:
        settings = get_settings()

    provider = (settings.vision_provider or "huggingface").strip().lower()
    if provider != "huggingface":
        return

    if hf_token_exists(settings):
        return

    raise MissingHuggingFaceTokenError(
        "HF_TOKEN is not set. "
        "When SENTINEL_VISION_PROVIDER=huggingface, create backend/.env from .env.example "
        "and set HF_TOKEN (Hugging Face access token). "
        "Optional: HF_MODEL and HF_API_URL. "
        "For local development without Hugging Face, set SENTINEL_VISION_PROVIDER=stub."
    )


_DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def parse_cors_origins(raw: str | None) -> list[str]:
    """Split a comma-separated CORS allowlist into normalized origin strings."""
    if not raw:
        return []
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


def resolve_cors_origins(settings: "Settings | None" = None) -> list[str]:
    """Build the effective CORS allowlist from settings and optional frontend URL."""
    if settings is None:
        settings = get_settings()

    origins = parse_cors_origins(settings.cors_origins)
    if settings.frontend_url:
        frontend_origin = settings.frontend_url.strip().rstrip("/")
        if frontend_origin and frontend_origin not in origins:
            origins.append(frontend_origin)
    return origins


_DEFAULT_VERCEL_CORS_ORIGIN_REGEX = r"https://vehicle-number-plate-detect.*\.vercel\.app"


def resolve_cors_origin_regex(settings: "Settings | None" = None) -> str | None:
    """Return the CORS origin regex, with a Vercel preview default in production."""
    if settings is None:
        settings = get_settings()

    configured = (settings.cors_origin_regex or "").strip()
    if configured:
        return configured

    if settings.env.strip().lower() == "production" and settings.frontend_url:
        frontend_origin = settings.frontend_url.strip().rstrip("/")
        if frontend_origin.endswith(".vercel.app"):
            return _DEFAULT_VERCEL_CORS_ORIGIN_REGEX
    return None


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
    api_port: int = Field(
        default=8080,
        validation_alias=AliasChoices("SENTINEL_API_PORT", "PORT"),
    )
    auth_jwt_secret: str = Field(default="dev-only-change-in-production")
    auth_jwt_issuer: str = Field(default="sentinel-anpr-ai")
    auth_access_token_ttl_seconds: int = Field(default=900)
    auth_refresh_token_ttl_seconds: int = Field(default=604800)
    upload_storage_dir: str = Field(default="data/uploads")
    report_storage_dir: str = Field(default="data/reports")
    # Comma-separated browser origins allowed to call the API (required for split deploy).
    cors_origins: str = Field(default=_DEFAULT_CORS_ORIGINS)
    # Optional single frontend URL (merged into CORS allowlist). Example: https://app.vercel.app
    frontend_url: str | None = Field(default=None)
    # Optional regex for extra origins (e.g. Vercel preview URLs: https://.*\.vercel\.app)
    cors_origin_regex: str | None = Field(default=None)

    # Vision provider: "huggingface" (Hugging Face Inference API) or "stub" (tests/local).
    vision_provider: str = Field(default="huggingface")
    hf_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices("HF_TOKEN", "SENTINEL_HF_TOKEN"),
    )
    hf_model: str = Field(
        default=_DEFAULT_HF_MODEL,
        validation_alias=AliasChoices("HF_MODEL", "SENTINEL_HF_MODEL"),
    )
    hf_api_url: str = Field(
        default=_DEFAULT_HF_API_URL,
        validation_alias=AliasChoices("HF_API_URL", "SENTINEL_HF_API_URL"),
    )
    hf_request_timeout_seconds: int = Field(default=60)
    # Vehicle detection provider: "opencv" (MobileNet-SSD) or "stub" (tests/local).
    vehicle_detection_provider: str = Field(default="opencv")
    # Chat assistant provider: "sarvam" (Sarvam AI API) or "stub" (local/tests).
    chat_provider: str = Field(default="sarvam")
    sarvam_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SARVAM_API_KEY", "SENTINEL_SARVAM_API_KEY"),
    )
    sarvam_api_url: str = Field(
        default=_DEFAULT_SARVAM_API_URL,
        validation_alias=AliasChoices("SARVAM_API_URL", "SENTINEL_SARVAM_API_URL"),
    )
    sarvam_model: str = Field(
        default=_DEFAULT_SARVAM_MODEL,
        validation_alias=AliasChoices("SARVAM_MODEL", "SENTINEL_SARVAM_MODEL"),
    )
    sarvam_request_timeout_seconds: int = Field(default=60)


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    load_env_file()
    return Settings()


def reload_settings() -> Settings:
    """Drop cached settings and reload from environment / .env."""
    get_settings.cache_clear()
    return get_settings()
