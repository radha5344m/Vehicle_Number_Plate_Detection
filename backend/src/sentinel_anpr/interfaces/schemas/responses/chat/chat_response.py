"""Chat API response schemas."""

from datetime import datetime

from pydantic import BaseModel


class ChatMessageData(BaseModel):
    """Assistant response payload."""

    role: str = "assistant"
    content: str
    model: str
    created_at: datetime


class ChatStreamChunkData(BaseModel):
    """Streaming chunk payload."""

    content: str
    done: bool = False
