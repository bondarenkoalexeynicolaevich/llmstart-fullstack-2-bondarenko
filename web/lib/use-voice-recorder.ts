"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type VoiceRecorderStatus = "idle" | "recording" | "processing";

function pickMimeType(): string | undefined {
  if (typeof MediaRecorder === "undefined") return undefined;
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
  ];
  return candidates.find((m) => MediaRecorder.isTypeSupported(m));
}

export function useVoiceRecorder() {
  const [status, setStatus] = useState<VoiceRecorderStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const resolveStopRef = useRef<((b: Blob | null) => void) | null>(null);

  const supported =
    typeof window !== "undefined" &&
    Boolean(navigator.mediaDevices?.getUserMedia) &&
    typeof MediaRecorder !== "undefined";

  useEffect(() => {
    return () => {
      const rec = mediaRecorderRef.current;
      if (rec && rec.state !== "inactive") {
        try {
          rec.stop();
        } catch {
          /* ignore */
        }
      }
      streamRef.current?.getTracks().forEach((t) => {
        t.stop();
      });
    };
  }, []);

  const start = useCallback(async () => {
    if (!supported) return;
    setError(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];
      const mime = pickMimeType();
      const rec = mime
        ? new MediaRecorder(stream, { mimeType: mime })
        : new MediaRecorder(stream);
      mediaRecorderRef.current = rec;

      rec.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      rec.onerror = () => {
        setError("Ошибка записи");
      };

      rec.onstop = () => {
        const parts = chunksRef.current;
        chunksRef.current = [];
        stream.getTracks().forEach((t) => {
          t.stop();
        });
        streamRef.current = null;
        mediaRecorderRef.current = null;

        const blob =
          parts.length > 0
            ? new Blob(parts, { type: rec.mimeType || "audio/webm" })
            : null;
        const resolve = resolveStopRef.current;
        resolveStopRef.current = null;
        setStatus("idle");
        resolve?.(blob);
      };

      rec.start(200);
      setStatus("recording");
    } catch {
      setError("Нет доступа к микрофону или устройство недоступно");
      setStatus("idle");
      streamRef.current?.getTracks().forEach((t) => {
        t.stop();
      });
      streamRef.current = null;
    }
  }, [supported]);

  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    const rec = mediaRecorderRef.current;
    if (!rec || rec.state === "inactive") {
      resolveStopRef.current?.(null);
      resolveStopRef.current = null;
      return null;
    }

    return new Promise<Blob | null>((resolve) => {
      resolveStopRef.current = resolve;
      try {
        rec.stop();
      } catch {
        resolveStopRef.current = null;
        resolve(null);
      }
    });
  }, []);

  const cancelRecording = useCallback(() => {
    const rec = mediaRecorderRef.current;
    if (rec && rec.state !== "inactive") {
      rec.onstop = () => {
        streamRef.current?.getTracks().forEach((t) => {
          t.stop();
        });
        streamRef.current = null;
        mediaRecorderRef.current = null;
        chunksRef.current = [];
        resolveStopRef.current?.(null);
        resolveStopRef.current = null;
      };
      try {
        rec.stop();
      } catch {
        /* ignore */
      }
    }
    setStatus("idle");
    setError(null);
  }, []);

  return {
    status,
    setStatus,
    error,
    setError,
    supported,
    start,
    stopRecording,
    cancelRecording,
  };
}
