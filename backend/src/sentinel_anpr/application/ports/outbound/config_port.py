"""Configuration access port."""

from typing import Protocol


class ConfigPort(Protocol):
    """Typed runtime configuration."""

    @property
    def app_name(self) -> str: ...

    @property
    def environment(self) -> str: ...

    @property
    def log_level(self) -> str: ...

    @property
    def database_url(self) -> str: ...

    def get(self, key: str, default: str | None = None) -> str | None: ...
