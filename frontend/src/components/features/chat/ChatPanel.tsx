import { useState } from "react";
import { Check, Copy, Send, Trash2, X } from "lucide-react";

import { MarkdownMessage } from "@/components/features/chat/MarkdownMessage";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { useChatAssistant } from "@/hooks/chat/useChatAssistant";
import { SUGGESTED_QUESTIONS } from "@/services/chatService";

interface ChatPanelProps {
  onClose: () => void;
}

function formatTime(value: string): string {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function CopyButton({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard may be unavailable.
    }
  }

  return (
    <button
      type="button"
      onClick={() => void handleCopy()}
      className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-slate-500 transition hover:bg-slate-100 hover:text-slate-700"
      aria-label="Copy response"
    >
      {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

export function ChatPanel({ onClose }: ChatPanelProps) {
  const { messages, input, setInput, isTyping, error, sendMessage, clearChat, bottomRef } =
    useChatAssistant();

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    void sendMessage(input);
  }

  return (
    <div className="flex h-[min(70vh,640px)] w-[min(92vw,380px)] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/15 sm:w-[400px]">
      <header className="flex items-start justify-between gap-3 border-b border-slate-200 bg-gradient-to-r from-brand to-blue-700 px-4 py-3 text-white">
        <div>
          <p className="text-sm font-semibold">Sentinel AI Assistant</p>
          <p className="text-xs text-blue-100">Powered by Sarvam AI</p>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={clearChat}
            className="rounded-lg p-2 text-blue-100 transition hover:bg-white/10 hover:text-white"
            aria-label="Clear chat"
            title="Clear chat"
          >
            <Trash2 className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-blue-100 transition hover:bg-white/10 hover:text-white"
            aria-label="Minimize chat"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </header>

      <div className="flex-1 space-y-3 overflow-y-auto px-3 py-4">
        {messages.length === 0 ? (
          <div className="space-y-3">
            <p className="text-sm text-slate-600">
              Ask about vehicle verification, investigation reports, risk levels, challans, and
              officer workflows.
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_QUESTIONS.map((question) => (
                <button
                  key={question}
                  type="button"
                  onClick={() => void sendMessage(question)}
                  className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-left text-xs text-slate-700 transition hover:border-brand/30 hover:bg-brand-soft hover:text-brand"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex flex-col gap-1 ${message.role === "user" ? "items-end" : "items-start"}`}
          >
            <div
              className={`max-w-[92%] rounded-2xl px-3 py-2 ${
                message.role === "user"
                  ? "bg-brand text-white"
                  : "border border-slate-200 bg-slate-50 text-slate-800"
              }`}
            >
              {message.role === "assistant" ? (
                <MarkdownMessage content={message.content || (isTyping ? "…" : "")} />
              ) : (
                <p className="text-sm leading-relaxed">{message.content}</p>
              )}
            </div>
            <div className="flex items-center gap-2 px-1">
              <span className="text-[10px] text-slate-400">{formatTime(message.createdAt)}</span>
              {message.role === "assistant" && message.content ? (
                <CopyButton content={message.content} />
              ) : null}
            </div>
          </div>
        ))}

        {isTyping && messages[messages.length - 1]?.role !== "assistant" ? (
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Spinner size="sm" />
            Assistant is typing…
          </div>
        ) : null}

        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 p-3">
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            rows={2}
            placeholder="Ask Sentinel AI Assistant…"
            className="max-h-28 min-h-[44px] flex-1 resize-none rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-brand focus:ring-2 focus:ring-brand/20"
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void sendMessage(input);
              }
            }}
          />
          <Button
            type="submit"
            size="sm"
            disabled={!input.trim() || isTyping}
            icon={isTyping ? <Spinner size="sm" /> : <Send className="h-4 w-4" />}
            aria-label="Send message"
          />
        </div>
      </form>
    </div>
  );
}
