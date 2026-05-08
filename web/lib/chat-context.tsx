"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { fetchDialogMessages, postDialogMessage, postVoiceDialogMessage } from "@/lib/api/dialog";
import type { DialogMessage } from "@/lib/api/types";
import { getSession } from "@/lib/session";

export type ChatStore = {
  messages: DialogMessage[];
  loading: boolean;
  loadError: string | null;
  sending: boolean;
  sendError: string | null;
  draft: string;
  online: boolean;
  sessionMissing: boolean;
  setDraft: (value: string) => void;
  loadHistory: () => Promise<void>;
  send: () => Promise<void>;
  sendVoice: (audio: Blob) => Promise<void>;
};

const ChatContext = createContext<ChatStore | null>(null);

function guessAudioFilename(blob: Blob): string {
  const t = blob.type || "";
  if (t.includes("webm")) return "recording.webm";
  if (t.includes("mp4")) return "recording.m4a";
  if (t.includes("ogg")) return "recording.ogg";
  return "recording.webm";
}

function useOnline(): boolean {
  const [online, setOnline] = useState(() =>
    typeof navigator !== "undefined" ? navigator.onLine : true,
  );

  useEffect(() => {
    const onOnline = () => {
      setOnline(true);
    };
    const onOffline = () => {
      setOnline(false);
    };
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  return online;
}

function readSessionParticipantFlow(): {
  participantId: string;
  flowId: string;
} | null {
  const s = getSession();
  const pid = s?.participant_id?.trim();
  const fid = s?.flow_id?.trim();
  if (!pid || !fid) return null;
  return { participantId: pid, flowId: fid };
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const [sessionCtx, setSessionCtx] = useState(() =>
    readSessionParticipantFlow(),
  );

  useEffect(() => {
    queueMicrotask(() => {
      setSessionCtx(readSessionParticipantFlow());
    });
  }, []);

  const sessionMissing = sessionCtx === null;
  const participantId = sessionCtx?.participantId ?? null;
  const flowId = sessionCtx?.flowId ?? null;

  const [messages, setMessages] = useState<DialogMessage[]>([]);
  const [loading, setLoading] = useState(() => sessionCtx !== null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [draft, setDraftState] = useState("");
  const online = useOnline();

  const loadHistory = useCallback(async () => {
    if (!participantId || !flowId) return;
    setLoading(true);
    setLoadError(null);
    try {
      const page = await fetchDialogMessages(participantId, flowId, 50);
      setMessages(page.items);
    } catch (e) {
      setLoadError(
        e instanceof Error ? e.message : "Не удалось загрузить историю",
      );
    } finally {
      setLoading(false);
    }
  }, [participantId, flowId]);

  useEffect(() => {
    if (!participantId || !flowId) return;
    queueMicrotask(() => {
      void loadHistory();
    });
  }, [participantId, flowId, loadHistory]);

  const setDraft = useCallback((value: string) => {
    setDraftState(value);
    setSendError(null);
  }, []);

  const send = useCallback(async () => {
    const text = draft.trim();
    if (!text || sending || !online || !participantId || !flowId) return;

    const optimisticId = `optimistic-${Date.now()}`;
    const optimisticUser: DialogMessage = {
      id: optimisticId,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setDraftState("");
    setSendError(null);
    setMessages((prev) => [...prev, optimisticUser]);
    setSending(true);
    try {
      const res = await postDialogMessage(participantId, flowId, text);
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== optimisticId);
        return [
          ...withoutTemp,
          {
            id: res.user_message_id,
            role: "user",
            content: text,
            created_at: new Date().toISOString(),
          },
          {
            id: res.assistant_message_id,
            role: "assistant",
            content: res.reply_text,
            created_at: new Date().toISOString(),
          },
        ];
      });
    } catch (e) {
      setMessages((prev) => prev.filter((m) => m.id !== optimisticId));
      setSendError(
        e instanceof Error ? e.message : "Не удалось отправить сообщение",
      );
    } finally {
      setSending(false);
    }
  }, [draft, sending, online, participantId, flowId]);

  const sendVoice = useCallback(
    async (audio: Blob) => {
      if (sending || !online || !participantId || !flowId) return;

      const optimisticId = `optimistic-voice-${Date.now()}`;
      const optimisticUser: DialogMessage = {
        id: optimisticId,
        role: "user",
        content: "…",
        created_at: new Date().toISOString(),
      };
      setSendError(null);
      setMessages((prev) => [...prev, optimisticUser]);
      setSending(true);
      try {
        const res = await postVoiceDialogMessage(
          flowId,
          audio,
          guessAudioFilename(audio),
        );
        const text =
          (res.transcription && res.transcription.trim()) || "голосовое сообщение";
        setMessages((prev) => {
          const withoutTemp = prev.filter((m) => m.id !== optimisticId);
          return [
            ...withoutTemp,
            {
              id: res.user_message_id,
              role: "user",
              content: text,
              created_at: new Date().toISOString(),
            },
            {
              id: res.assistant_message_id,
              role: "assistant",
              content: res.reply_text,
              created_at: new Date().toISOString(),
            },
          ];
        });
      } catch (e) {
        setMessages((prev) => prev.filter((m) => m.id !== optimisticId));
        setSendError(
          e instanceof Error ? e.message : "Не удалось отправить голосовое",
        );
      } finally {
        setSending(false);
      }
    },
    [sending, online, participantId, flowId],
  );

  const value = useMemo<ChatStore>(
    () => ({
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
    }),
    [
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
    ],
  );

  return (
    <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
  );
}

export function useChatStore(): ChatStore {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error("useChatStore must be used within ChatProvider");
  }
  return ctx;
}
