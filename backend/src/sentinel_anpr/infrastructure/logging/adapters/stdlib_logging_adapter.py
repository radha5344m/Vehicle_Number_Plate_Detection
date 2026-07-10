"""Standard library logging adapter."""

import logging
from typing import Any

from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort
from sentinel_anpr.infrastructure.logging.context import correlation_id_var


class StdlibLoggingAdapter(LoggingPort):
    """Implements LoggingPort using structured standard logging."""

    def __init__(self, name: str = "sentinel_anpr") -> None:
        self._logger = logging.getLogger(name)

    def _with_context(self, context: dict[str, Any]) -> dict[str, Any]:
        correlation_id = correlation_id_var.get()
        if correlation_id:
            return {**context, "correlation_id": correlation_id}
        return context

    def debug(self, message: str, **context: Any) -> None:
        self._logger.debug(message, extra=self._with_context(context))

    def info(self, message: str, **context: Any) -> None:
        self._logger.info(message, extra=self._with_context(context))

    def warning(self, message: str, **context: Any) -> None:
        self._logger.warning(message, extra=self._with_context(context))

    def error(self, message: str, **context: Any) -> None:
        self._logger.error(message, extra=self._with_context(context))
