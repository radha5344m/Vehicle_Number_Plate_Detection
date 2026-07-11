"""Sarvam AI chat completions adapter."""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from typing import Any

import httpx

from sentinel_anpr.application.dto.chat_dto import ChatMessageDto, ChatStreamChunkDto
from sentinel_anpr.application.ports.outbound.chat_service_port import ChatServicePort
from sentinel_anpr.application.ports.outbound.logging_port import LoggingPort


class SarvamChatService(ChatServicePort):
    """Call Sarvam AI OpenAI-compatible chat completions API."""

    def __init__(
        self,
        *,
        api_key: str,
        api_url: str,
        model: str,
        request_timeout_seconds: int,
        logger: LoggingPort,
        client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._api_url = api_url.rstrip("/")
        self._model = model
        self._timeout = request_timeout_seconds
        self._logger = logger
        self._client = client or httpx.Client(timeout=request_timeout_seconds)

    @property
    def model_name(self) -> str:
        return self._model

    def complete(self, messages: Sequence[ChatMessageDto]) -> str:
        payload = self._build_payload(messages, stream=False)
        response = self._client.post(
            self._api_url,
            headers=self._headers(),
            json=payload,
        )
        if response.is_error:
            self._raise_api_error(response)
        data = response.json()
        content = self._extract_content(data)
        if content:
            return content
        raise RuntimeError("Sarvam AI returned an empty response. Please try again.")

    def stream(self, messages: Sequence[ChatMessageDto]) -> Iterator[ChatStreamChunkDto]:
        payload = self._build_payload(messages, stream=True)
        with self._client.stream(
            "POST",
            self._api_url,
            headers=self._headers(),
            json=payload,
        ) as response:
            if response.is_error:
                response.read()
                self._raise_api_error(response)
            accumulated = ""
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    data_part = line.removeprefix("data:").strip()
                else:
                    data_part = line.strip()
                if not data_part or data_part == "[DONE]":
                    if data_part == "[DONE]":
                        break
                    continue
                try:
                    payload_json = json.loads(data_part)
                except json.JSONDecodeError:
                    self._logger.debug(
                        "sarvam_stream_parse_skip",
                        detail=f"Unparseable SSE chunk: {data_part[:80]}",
                    )
                    continue
                content = self._extract_delta(payload_json)
                if content:
                    accumulated += content
                    yield ChatStreamChunkDto(content=content, done=False)
            if not accumulated.strip():
                # Sarvam may stream reasoning tokens only; fall back to a full completion.
                fallback = self.complete(messages)
                if fallback:
                    yield ChatStreamChunkDto(content=fallback, done=False)
        yield ChatStreamChunkDto(content="", done=True)

    def _raise_api_error(self, response: httpx.Response) -> None:
        message = f"Sarvam API error ({response.status_code})"
        try:
            body = response.json()
            error = body.get("error") if isinstance(body, dict) else None
            if isinstance(error, dict) and error.get("message"):
                message = str(error["message"])
        except Exception:
            pass
        raise RuntimeError(message)

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "api-subscription-key": self._api_key,
        }

    def _build_payload(self, messages: Sequence[ChatMessageDto], *, stream: bool) -> dict[str, Any]:
        return {
            "model": self._model,
            "messages": [{"role": message.role, "content": message.content} for message in messages],
            "temperature": 0.4,
            "max_tokens": 4096,
            "stream": stream,
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        return ""

    @staticmethod
    def _extract_delta(data: dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        delta = choices[0].get("delta") or {}
        content = delta.get("content")
        if content is None:
            return ""
        return str(content)
