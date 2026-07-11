"""Chat assistant unit tests."""

from sentinel_anpr.application.dto.chat_dto import ChatMessageDto, SendChatMessageCommand
from sentinel_anpr.application.use_cases.chat.send_chat_message_use_case import SendChatMessageUseCase
from sentinel_anpr.infrastructure.ai.stub_chat_service import StubChatService


def test_send_chat_message_use_case_returns_assistant_response() -> None:
    use_case = SendChatMessageUseCase(chat_service=StubChatService())
    result = use_case.execute(
        SendChatMessageCommand(
            officer_id="officer-1",
            officer_role="POLICE_OFFICER",
            messages=(ChatMessageDto(role="user", content="What does High Risk mean?"),),
        )
    )
    assert "High Risk" in result.content
    assert result.model == "stub-assistant"


def test_send_chat_message_use_case_streams_chunks() -> None:
    use_case = SendChatMessageUseCase(chat_service=StubChatService())
    chunks = list(
        use_case.stream(
            SendChatMessageCommand(
                officer_id="officer-1",
                officer_role="POLICE_OFFICER",
                messages=(ChatMessageDto(role="user", content="How do I generate a challan?"),),
            )
        )
    )
    assert chunks
    assert chunks[-1].done is True
    assert "challan" in "".join(chunk.content for chunk in chunks).lower()
