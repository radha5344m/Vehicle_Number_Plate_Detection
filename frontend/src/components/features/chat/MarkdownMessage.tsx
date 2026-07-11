import type { ReactNode } from "react";

interface MarkdownMessageProps {
  content: string;
}

function renderInline(text: string): ReactNode[] {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={index}
          className="rounded bg-slate-200 px-1 py-0.5 font-mono text-[0.85em] text-slate-800"
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={index} className="font-semibold text-slate-900">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <span key={index}>{part}</span>;
  });
}

export function MarkdownMessage({ content }: MarkdownMessageProps) {
  const blocks = content.split(/\n```/);

  return (
    <div className="space-y-2 text-sm leading-relaxed text-slate-700">
      {blocks.map((block, blockIndex) => {
        if (blockIndex > 0) {
          const [languageLine, ...rest] = block.split("\n");
          const code = rest.join("\n").replace(/```$/, "");
          return (
            <pre
              key={`code-${blockIndex}`}
              className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs text-slate-100"
            >
              <code>{languageLine ? `// ${languageLine}\n` : ""}{code}</code>
            </pre>
          );
        }

        return block.split("\n").map((line, lineIndex) => {
          const trimmed = line.trim();
          if (!trimmed) {
            return <div key={`spacer-${lineIndex}`} className="h-2" />;
          }
          if (trimmed.startsWith("- ")) {
            return (
              <p key={`line-${lineIndex}`} className="pl-3">
                • {renderInline(trimmed.slice(2))}
              </p>
            );
          }
          if (/^\d+\.\s/.test(trimmed)) {
            return (
              <p key={`line-${lineIndex}`} className="pl-3">
                {renderInline(trimmed)}
              </p>
            );
          }
          return <p key={`line-${lineIndex}`}>{renderInline(trimmed)}</p>;
        });
      })}
    </div>
  );
}
