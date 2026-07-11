import { env } from "@/config/env";
import { getAccessToken } from "@/stores/authStore";
import { monitoredFetch } from "@/services/api/monitoredFetch";
import { postApiData } from "@/services/api/httpClient";

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
}

export interface ChatCompletionResponse {
  role: "assistant";
  content: string;
  model: string;
  created_at: string;
}

export interface ChatStreamChunk {
  content: string;
  done: boolean;
}

export const SUGGESTED_QUESTIONS = [
  "Explain this investigation report",
  "What does High Risk mean?",
  "How do I verify multiple vehicles?",
  "Why was this vehicle flagged?",
  "How do I generate a challan?",
  "How do I upload multiple vehicles?",
] as const;

function buildApiUrl(path: string): string {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

function toApiMessages(messages: ChatMessage[]) {
  return messages.map((message) => ({
    role: message.role,
    content: message.content,
  }));
}

export const chatService = {
  async sendMessage(messages: ChatMessage[], signal?: AbortSignal): Promise<ChatCompletionResponse> {
    return postApiData<ChatCompletionResponse>("/v1/chat/messages", {
      messages: toApiMessages(messages),
      stream: false,
    });
  },

  async *streamMessage(
    messages: ChatMessage[],
    signal?: AbortSignal,
  ): AsyncGenerator<ChatStreamChunk> {
    const token = getAccessToken()?.trim();
    const response = await monitoredFetch(buildApiUrl("/v1/chat/messages"), {
      method: "POST",
      headers: {
        Accept: "text/event-stream",
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        messages: toApiMessages(messages),
        stream: true,
      }),
      signal,
    });

    if (!response.ok) {
      throw new Error(`Chat request failed (${response.status})`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Streaming is not supported in this browser.");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) continue;
        const payload = trimmed.slice(5).trim();
        if (!payload || payload === "[DONE]") {
          if (payload === "[DONE]") {
            yield { content: "", done: true };
          }
          continue;
        }
        try {
          const chunk = JSON.parse(payload) as ChatStreamChunk;
          yield chunk;
        } catch {
          // Ignore malformed SSE chunks.
        }
      }
    }

    yield { content: "", done: true };
  },
};
