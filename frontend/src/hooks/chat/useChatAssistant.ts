import { useCallback, useEffect, useRef, useState } from "react";

import { chatService, type ChatMessage } from "@/services/chatService";

function createMessage(role: ChatMessage["role"], content: string): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function useChatAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const clearChat = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
    setInput("");
    setError(null);
    setIsTyping(false);
  }, []);

  const sendMessage = useCallback(
    async (rawContent: string) => {
      const content = rawContent.trim();
      if (!content || isTyping) return;

      const userMessage = createMessage("user", content);
      const nextMessages = [...messages, userMessage];
      setMessages(nextMessages);
      setInput("");
      setError(null);
      setIsTyping(true);

      const assistantId = crypto.randomUUID();
      const assistantPlaceholder = createMessage("assistant", "");
      assistantPlaceholder.id = assistantId;
      setMessages((current) => [...current, assistantPlaceholder]);

      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        let accumulated = "";
        for await (const chunk of chatService.streamMessage(nextMessages, controller.signal)) {
          if (chunk.content) {
            accumulated += chunk.content;
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId ? { ...message, content: accumulated } : message,
              ),
            );
          }
          if (chunk.done) break;
        }

        if (!accumulated.trim()) {
          const fallback = await chatService.sendMessage(nextMessages, controller.signal);
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantId
                ? { ...message, content: fallback.content, createdAt: fallback.created_at }
                : message,
            ),
          );
        }
      } catch (err) {
        if (controller.signal.aborted) return;
        const message = err instanceof Error ? err.message : "Failed to reach Sentinel AI Assistant.";
        setError(message);
        setMessages((current) => current.filter((item) => item.id !== assistantId));
      } finally {
        setIsTyping(false);
      }
    },
    [isTyping, messages],
  );

  return {
    messages,
    input,
    setInput,
    isTyping,
    error,
    sendMessage,
    clearChat,
    bottomRef,
  };
}
