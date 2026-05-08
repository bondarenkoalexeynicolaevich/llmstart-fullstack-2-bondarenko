import type { Metadata } from "next";

import { ChatPanel } from "@/components/chat-panel";

export const metadata: Metadata = {
  title: "Чат | LMStart",
};

export default function ChatPage() {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <div className="flex flex-col gap-1 shrink-0">
        <h1 className="text-xl font-semibold tracking-tight">Чат</h1>
        <p className="text-sm text-muted-foreground">
          Диалог с ассистентом; состояние синхронизировано с плавающим виджетом.
        </p>
      </div>
      <div className="flex min-h-0 flex-1 flex-col rounded-lg border border-border bg-card/30 p-4">
        <ChatPanel />
      </div>
    </div>
  );
}
