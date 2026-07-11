"""Resolve the active chat service from current environment settings."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import TYPE_CHECKING

from sentinel_anpr.application.dto.chat_dto import ChatMessageDto, ChatStreamChunkDto
from sentinel_anpr.application.ports.outbound.chat_service_port import ChatServicePort
from sentinel_anpr.infrastructure.config.settings import reload_settings

if TYPE_CHECKING:
    from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort


class ChatServiceProvider(ChatServicePort):
    """Build the chat adapter from fresh settings on each request.

    This avoids stale stub-mode instances when ``backend/.env`` is updated while
    the API process is still running.
    """

    def __init__(
        self,
        *,
        build_chat_service: Callable[..., ChatServicePort],
        logger: LoggingPort,
    ) -> None:
        self._build_chat_service = build_chat_service
        self._logger = logger
        self._delegate: ChatServicePort | None = None
        self._delegate_model = "uninitialized"

    @property
    def model_name(self) -> str:
        return self._delegate_model

    def complete(self, messages: Sequence[ChatMessageDto]) -> str:
        return self._get_delegate().complete(messages)

    def stream(self, messages: Sequence[ChatMessageDto]) -> Iterator[ChatStreamChunkDto]:
        yield from self._get_delegate().stream(messages)

    def _get_delegate(self) -> ChatServicePort:
        settings = reload_settings()
        delegate = self._build_chat_service(settings=settings, logger=self._logger)
        self._delegate = delegate
        self._delegate_model = delegate.model_name
        return delegate
