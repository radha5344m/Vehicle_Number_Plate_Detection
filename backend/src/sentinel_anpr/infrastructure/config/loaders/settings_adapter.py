"""Settings adapter implementing ConfigPort."""

from sentinel_anpr.application.ports.outbound.config_port import ConfigPort
from sentinel_anpr.infrastructure.config.settings import Settings


class SettingsConfigAdapter(ConfigPort):
    """Maps pydantic Settings to ConfigPort."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def app_name(self) -> str:
        return self._settings.app_name

    @property
    def environment(self) -> str:
        return self._settings.env

    @property
    def log_level(self) -> str:
        return self._settings.log_level

    @property
    def database_url(self) -> str:
        return self._settings.database_url

    def get(self, key: str, default: str | None = None) -> str | None:
        return getattr(self._settings, key, default)
