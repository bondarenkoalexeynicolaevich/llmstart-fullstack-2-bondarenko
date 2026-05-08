"use client";

import { BarChart3, Mic, Square } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { postDataQuery } from "@/lib/api/data-query";
import type { DialogMessage } from "@/lib/api/types";
import { useChatStore } from "@/lib/chat-context";
import { getSession } from "@/lib/session";
import { useVoiceRecorder } from "@/lib/use-voice-recorder";
import { cn } from "@/lib/utils";

type DataAssistantBubble = {
  id: string;
  kind: "data_assistant";
  explanation: string;
  correlationId?: string;
  rows: Record<string, unknown>[];
};

type LocalUserBubble = { id: string; kind: "local_user"; content: string };

type LocalBubble = LocalUserBubble | DataAssistantBubble;

function mapDataQueryError(error: unknown): string {
  const s =
    error instanceof Error ? error.message : String(error).slice(0, 500);
  const low = s.toLowerCase();
  if (low.includes("unrecognized_intent"))
    return "Вопрос не распознан. Попробуйте переформулировать.";
  if (low.includes("flow_not_found") || low.includes("flow not found")) {
    return "Поток не найден в базе (404). Проверьте: выполнен ли `make db-seed`, и совпадает ли UUID потока при входе с тем, что в БД (`00000000-…` после сидов). Выйдите из сессии и войдите снова.";
  }
  if (
    low.includes("(forbidden)") ||
    low.includes("operation not allowed") ||
    low.includes("ошибка 403") ||
    low.endsWith("(403)")
  ) {
    return "Нет доступа (403): режим данных только для учителя; либо `flow_id` в токене не совпадает с потоком в URL.";
  }
  return s;
}

function ResultTable({ rows }: { rows: Record<string, unknown>[] }) {
  if (rows.length === 0)
    return (
      <p className="mt-2 text-xs text-muted-foreground">Нет строк в ответе.</p>
    );
  const cols = Array.from(
    rows.reduce((acc, row) => {
      Object.keys(row).forEach((k) => {
        acc.add(k);
      });
      return acc;
    }, new Set<string>()),
  );
  return (
    <div className="mt-2 max-h-48 overflow-auto rounded-md border border-border/60 bg-background/50">
      <table className="w-full border-collapse text-left text-xs tabular-nums">
        <thead className="sticky top-0 bg-muted/60">
          <tr>
            {cols.map((c) => (
              <th
                key={c}
                className="border-b border-border px-2 py-1 font-medium whitespace-nowrap"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIdx) => (
            <tr
              key={`${rowIdx}:${cols.map((c) => renderCell(row[c])).join(":")}`}
              className="border-b border-border/40 last:border-0"
            >
              {cols.map((c) => (
                <td key={c} className="break-all px-2 py-1">
                  {renderCell(row[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderCell(v: unknown): string {
  if (v == null) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export function ChatPanel() {
  const {
    messages,
    loading,
    loadError,
    sending,
    sendError,
    draft,
    online,
    sessionMissing,
    setDraft,
    loadHistory,
    send,
    sendVoice,
  } = useChatStore();

  const voice = useVoiceRecorder();
  const [dataMode, setDataMode] = useState(false);
  const [localBubbles, setLocalBubbles] = useState<LocalBubble[]>([]);
  const [queryBusy, setQueryBusy] = useState(false);

  const [clientReady, setClientReady] = useState(false);
  useEffect(() => {
    setClientReady(true);
  }, []);

  const teacher =
    clientReady && !sessionMissing && getSession()?.role === "teacher";

  const listEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, localBubbles]);

  const isRecording = voice.status === "recording";

  const onVoiceClick = useCallback(async () => {
    if (!voice.supported || sending || queryBusy || !online || dataMode) return;
    voice.setError(null);
    if (isRecording) {
      const blob = await voice.stopRecording();
      if (blob && blob.size > 0) {
        await sendVoice(blob);
      }
      return;
    }
    await voice.start();
  }, [
    voice,
    isRecording,
    sending,
    queryBusy,
    online,
    sendVoice,
    dataMode,
  ]);

  const micDisabled =
    sending ||
    queryBusy ||
    !online ||
    loading ||
    Boolean(loadError) ||
    !voice.supported ||
    dataMode;

  const onSendCombined = async () => {
    const text = draft.trim();
    if (!text || sending || queryBusy || !online) return;

    const flowId = getSession()?.flow_id;
    if (dataMode) {
      if (!flowId || !teacher) return;
      const uid = `dq-user-${Date.now()}`;
      setLocalBubbles((b) => [...b, { id: uid, kind: "local_user", content: text }]);
      setDraft("");
      setQueryBusy(true);
      try {
        const res = await postDataQuery(flowId, text);
        const aid = `dq-asst-${Date.now()}`;
        setLocalBubbles((b) => [
          ...b,
          {
            id: aid,
            kind: "data_assistant",
            explanation: res.explanation,
            correlationId: res.correlation_id,
            rows: res.result ?? [],
          },
        ]);
      } catch (e) {
        const aid = `dq-err-${Date.now()}`;
        setLocalBubbles((b) => [
          ...b,
          {
            id: aid,
            kind: "data_assistant",
            explanation: mapDataQueryError(e),
            rows: [],
          },
        ]);
      } finally {
        setQueryBusy(false);
      }
      return;
    }
    await send();
  };

  if (sessionMissing) {
    return (
      <p className="text-muted-foreground">
        Войдите, чтобы использовать чат.
      </p>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-1 flex-col gap-2 py-2" aria-busy="true">
        <div className="h-10 animate-pulse rounded-md bg-muted" />
        <div className="h-10 animate-pulse rounded-md bg-muted" />
        <div className="h-10 w-3/4 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex flex-1 flex-col gap-3 py-2">
        <div
          className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive"
          role="alert"
        >
          {loadError}
        </div>
        <Button
          type="button"
          variant="secondary"
          onClick={() => {
            void loadHistory();
          }}
        >
          Повторить загрузку
        </Button>
      </div>
    );
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3">
      {!online ? (
        <p className="text-xs text-amber-600 dark:text-amber-500" role="status">
          Нет сети. Отправка недоступна.
        </p>
      ) : null}
      {dataMode && teacher ? (
        <p className="text-xs text-muted-foreground" role="status">
          Режим данных: задаёте вопрос по статистике потока (только преподаватель).
        </p>
      ) : null}

      <div className="min-h-0 flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && localBubbles.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Нет сообщений. Напишите ассистенту.
          </p>
        ) : null}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {localBubbles.map((lb) =>
          lb.kind === "local_user" ? (
            <div key={lb.id} className="flex justify-end">
              <div className="max-w-[85%] whitespace-pre-wrap break-words rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground">
                {lb.content}
              </div>
            </div>
          ) : (
            <div key={lb.id} className="flex justify-start">
              <div className="max-w-[92%] rounded-lg border border-border bg-muted/50 px-3 py-2 text-sm text-foreground">
                <div className="whitespace-pre-wrap break-words">
                  {lb.explanation}
                </div>
                {lb.correlationId !== undefined && lb.correlationId !== "" ? (
                  <p className="mt-1 text-[10px] text-muted-foreground tabular-nums">
                    correlation: {lb.correlationId.slice(0, 8)}…
                  </p>
                ) : null}
                {(lb.rows.length > 0 ||
                  (lb.correlationId !== undefined &&
                    lb.correlationId !== "")) && (
                  <ResultTable rows={lb.rows} />
                )}
              </div>
            </div>
          ),
        )}
        <div ref={listEndRef} />
      </div>

      {sendError ? (
        <p className="text-sm text-destructive" role="alert">
          {sendError}
        </p>
      ) : null}

      {voice.error ? (
        <p className="text-xs text-amber-600 dark:text-amber-500" role="status">
          {voice.error}
        </p>
      ) : null}

      <div className="flex shrink-0 items-end gap-2 border-t border-border pt-3">
        <textarea
          value={draft}
          onChange={(e) => {
            setDraft(e.target.value);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void onSendCombined();
            }
          }}
          disabled={sending || queryBusy || !online || isRecording}
          rows={3}
          placeholder={
            dataMode && teacher
              ? "Задайте вопрос по данным потока… (Shift+Enter — новая строка)"
              : "Сообщение… (Shift+Enter — новая строка)"
          }
          className={cn(
            "min-h-0 min-w-0 w-full flex-1 resize-y rounded-lg border border-input bg-transparent px-2.5 py-2 text-base transition-colors outline-none",
            "placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
            "disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50",
            "md:text-sm dark:bg-input/30 dark:disabled:bg-input/80",
          )}
          aria-label="Текст сообщения"
        />
        {teacher ? (
          <Button
            type="button"
            variant={dataMode ? "secondary" : "outline"}
            size="icon"
            className={cn("shrink-0", dataMode && "ring-2 ring-ring")}
            title={
              dataMode
                ? "Выйти из режима данных"
                : "Режим вопроса к данным БД потока"
            }
            aria-pressed={dataMode}
            onClick={() => {
              setDataMode((x) => !x);
              voice.setError(null);
            }}
            disabled={queryBusy || isRecording || !online}
          >
            <BarChart3 className="h-4 w-4" aria-hidden />
          </Button>
        ) : null}
        <Button
          type="button"
          variant={isRecording ? "destructive" : "outline"}
          size="icon"
          className={cn("shrink-0", isRecording && "animate-pulse")}
          aria-label={
            isRecording ? "Остановить запись и отправить" : "Запись с микрофона"
          }
          title={
            !voice.supported
              ? "Микрофон недоступен в этом браузере"
              : isRecording
                ? "Остановить и отправить"
                : "Голосовое сообщение"
          }
          onClick={() => {
            void onVoiceClick();
          }}
          disabled={micDisabled && !isRecording}
        >
          {isRecording ? (
            <Square className="h-4 w-4 fill-current" aria-hidden />
          ) : (
            <Mic className="h-4 w-4" aria-hidden />
          )}
        </Button>
        <Button
          type="button"
          className="shrink-0 self-end"
          onClick={() => {
            void onSendCombined();
          }}
          disabled={
            sending ||
            queryBusy ||
            !draft.trim() ||
            !online ||
            isRecording ||
            (dataMode && !teacher)
          }
        >
          {sending || queryBusy ? "Отправка…" : "Отправить"}
        </Button>
      </div>
    </div>
  );
}

function MessageBubble({ message: m }: { message: DialogMessage }) {
  const isUser = m.role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] whitespace-pre-wrap break-words rounded-lg px-3 py-2 text-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "border border-border bg-muted/50 text-foreground",
        )}
      >
        {m.content}
      </div>
    </div>
  );
}
