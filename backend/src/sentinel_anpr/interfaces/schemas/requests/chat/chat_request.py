"""Chat API request schemas."""

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Single chat message in a conversation."""

    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=8000)


class SendChatMessageRequest(BaseModel):
    """Send a message to the Sentinel AI Assistant."""

    messages: list[ChatMessageRequest] = Field(min_length=1, max_length=40)
    stream: bool = False
