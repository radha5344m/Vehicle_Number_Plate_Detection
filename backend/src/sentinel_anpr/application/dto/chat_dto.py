"""Chat assistant DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChatMessageDto:
    """Single chat message."""

    role: str
    content: str


@dataclass(frozen=True)
class SendChatMessageCommand:
    """Inbound chat request from an authenticated officer."""

    officer_id: str
    officer_role: str
    messages: tuple[ChatMessageDto, ...]


@dataclass(frozen=True)
class SendChatMessageResult:
    """Completed chat response."""

    content: str
    model: str
    created_at: datetime


@dataclass(frozen=True)
class ChatStreamChunkDto:
    """Streaming token delta."""

    content: str
    done: bool = False
