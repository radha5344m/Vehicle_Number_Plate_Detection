"""Outbound port for AI chat completions."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol

from sentinel_anpr.application.dto.chat_dto import ChatMessageDto, ChatStreamChunkDto


class ChatServicePort(Protocol):
    """Generate assistant responses via an external LLM provider."""

    @property
    def model_name(self) -> str:
        """Configured model identifier."""
        ...

    def complete(self, messages: Sequence[ChatMessageDto]) -> str:
        """Return a full assistant response."""
        ...

    def stream(self, messages: Sequence[ChatMessageDto]) -> Iterator[ChatStreamChunkDto]:
        """Yield incremental assistant response chunks."""
        ...
