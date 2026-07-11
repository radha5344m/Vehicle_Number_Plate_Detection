"""Sentinel AI Assistant chat routes."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from sentinel_anpr.application.dto.auth_dto import AuthPrincipal
from sentinel_anpr.application.dto.chat_dto import ChatMessageDto, SendChatMessageCommand
from sentinel_anpr.application.use_cases.chat.send_chat_message_use_case import SendChatMessageUseCase
from sentinel_anpr.interfaces.rest_api.v1.dependencies.auth import get_current_principal
from sentinel_anpr.interfaces.rest_api.v1.errors.error_response_builder import build_error_response
from sentinel_anpr.interfaces.schemas.requests.chat.chat_request import SendChatMessageRequest
from sentinel_anpr.interfaces.schemas.responses.chat.chat_response import ChatMessageData, ChatStreamChunkData
from sentinel_anpr.interfaces.schemas.responses.common.envelope import ApiResponse, ResponseMeta

router = APIRouter(prefix="/chat", tags=["chat"])


def _to_command(body: SendChatMessageRequest, principal: AuthPrincipal) -> SendChatMessageCommand:
    return SendChatMessageCommand(
        officer_id=principal.officer_id,
        officer_role=principal.role,
        messages=tuple(
            ChatMessageDto(role=message.role, content=message.content.strip())
            for message in body.messages
        ),
    )


@router.post("/messages", response_model=ApiResponse[ChatMessageData])
async def send_chat_message(
    request: Request,
    body: SendChatMessageRequest,
    principal: AuthPrincipal = Depends(get_current_principal),
) -> ApiResponse[ChatMessageData] | JSONResponse | StreamingResponse:
    """Send a message to the Sentinel AI Assistant."""
    if body.stream:
        return await _stream_chat_message(request, body, principal)

    try:
        correlation_id = getattr(request.state, "correlation_id", None) or str(uuid.uuid4())
        use_case: SendChatMessageUseCase = request.app.state.container.send_chat_message_use_case
        result = use_case.execute(_to_command(body, principal))
        return ApiResponse(
            data=ChatMessageData(
                content=result.content,
                model=result.model,
                created_at=result.created_at,
            ),
            meta=ResponseMeta(correlation_id=correlation_id),
        )
    except Exception as exc:
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Chat assistant request failed.",
            log_level="error",
            exc=exc,
        )


async def _stream_chat_message(
    request: Request,
    body: SendChatMessageRequest,
    principal: AuthPrincipal,
) -> StreamingResponse | JSONResponse:
    try:
        use_case: SendChatMessageUseCase = request.app.state.container.send_chat_message_use_case
        command = _to_command(body, principal)

        async def event_generator() -> AsyncIterator[str]:
            for chunk in use_case.stream(command):
                payload = ChatStreamChunkData(content=chunk.content, done=chunk.done)
                yield f"data: {json.dumps(payload.model_dump())}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as exc:
        return build_error_response(
            request,
            500,
            "INTERNAL_ERROR",
            "Chat assistant streaming failed.",
            log_level="error",
            exc=exc,
        )
