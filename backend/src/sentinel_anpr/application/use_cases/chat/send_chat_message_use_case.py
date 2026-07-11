"""Send chat messages to the Sentinel AI Assistant."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

from sentinel_anpr.application.dto.chat_dto import (
    ChatMessageDto,
    ChatStreamChunkDto,
    SendChatMessageCommand,
    SendChatMessageResult,
)
from sentinel_anpr.application.ports.outbound.chat_service_port import ChatServicePort
from sentinel_anpr.domain.assistant.policies.sentinel_assistant_system_prompt import (
    SENTINEL_ASSISTANT_SYSTEM_PROMPT,
)


class SendChatMessageUseCase:
    """Orchestrate Sentinel AI Assistant conversations."""

    def __init__(self, chat_service: ChatServicePort) -> None:
        self._chat_service = chat_service

    def execute(self, command: SendChatMessageCommand) -> SendChatMessageResult:
        messages = self._build_messages(command)
        content = self._chat_service.complete(messages)
        return SendChatMessageResult(
            content=content,
            model=self._chat_service.model_name,
            created_at=datetime.now(UTC),
        )

    def stream(self, command: SendChatMessageCommand) -> Iterator[ChatStreamChunkDto]:
        messages = self._build_messages(command)
        yield from self._chat_service.stream(messages)

    def _build_messages(self, command: SendChatMessageCommand) -> tuple[ChatMessageDto, ...]:
        role_context = (
            f"The current officer role is {command.officer_role}. "
            "Tailor guidance to their permissions and responsibilities."
        )
        system_content = f"{SENTINEL_ASSISTANT_SYSTEM_PROMPT}\n\n{role_context}"
        return (
            ChatMessageDto(role="system", content=system_content),
            *command.messages,
        )
