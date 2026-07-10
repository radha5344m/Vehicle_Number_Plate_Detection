"""Logging port."""

from typing import Any, Protocol


class LoggingPort(Protocol):
    """Structured application logging."""

    def debug(self, message: str, **context: Any) -> None: ...

    def info(self, message: str, **context: Any) -> None: ...

    def warning(self, message: str, **context: Any) -> None: ...

    def error(self, message: str, **context: Any) -> None: ...
