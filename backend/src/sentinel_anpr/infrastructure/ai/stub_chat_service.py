"""Deterministic chat stub for tests and local development without Sarvam credentials."""

from __future__ import annotations

from collections.abc import Iterator, Sequence

from sentinel_anpr.application.dto.chat_dto import ChatMessageDto, ChatStreamChunkDto
from sentinel_anpr.application.ports.outbound.chat_service_port import ChatServicePort


class StubChatService(ChatServicePort):
    """Return canned Sentinel assistant responses without calling external APIs."""

    def __init__(self, model: str = "stub-assistant") -> None:
        self._model = model

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, messages: Sequence[ChatMessageDto]) -> str:
        user_message = ""
        for message in reversed(messages):
            if message.role == "user":
                user_message = message.content
                break
        return self._stub_response(user_message)

    def stream(self, messages: Sequence[ChatMessageDto]) -> Iterator[ChatStreamChunkDto]:
        response = self.complete(messages)
        chunk_size = 24
        for index in range(0, len(response), chunk_size):
            yield ChatStreamChunkDto(content=response[index : index + chunk_size], done=False)
        yield ChatStreamChunkDto(content="", done=True)

    @staticmethod
    def _stub_response(user_message: str) -> str:
        lowered = user_message.lower()
        if "high risk" in lowered:
            return (
                "**High Risk** means the investigation found strong indicators of suspicious activity — "
                "such as major attribute mismatches, registry flags, or multiple risk signals. "
                "Review the investigation report details and escalate per department protocol."
            )
        if "challan" in lowered:
            return (
                "To **generate a challan**:\n"
                "1. Open **e-Challan** from the sidebar.\n"
                "2. Search the registration number or start from an investigation.\n"
                "3. Select the violation, confirm details, and issue the challan."
            )
        if "multiple vehicle" in lowered or "verify multiple" in lowered:
            return (
                "To **verify multiple vehicles**:\n"
                "1. Upload the scene image on Vehicle Verification.\n"
                "2. Adjust the detection rectangles so each box covers one vehicle.\n"
                "3. Click verify — each rectangle runs an independent investigation."
            )
        return (
            "I'm the Sentinel AI Assistant (stub mode). "
            "Configure `SARVAM_API_KEY` in `backend/.env` for full Sarvam AI responses. "
            "I can help with vehicle verification, investigation reports, risk levels, challans, and workflows."
        )
