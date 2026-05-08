import type { WebClientSession, WebSessionCreateResponse } from "@/lib/types";
import {
  claimString,
  decodeJwtPayload,
  isJwtExpiredByPayload,
} from "@/lib/jwt-decode";

const STORAGE_KEY = "llmstart_web_v1";

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function getSession(): WebClientSession | null {
  if (!isBrowser()) return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw) as WebClientSession;
    const token =
      typeof data?.access_token === "string" ? data.access_token.trim() : "";
    if (!token) {
      return null;
    }

    const payload = decodeJwtPayload(token);
    if (payload && isJwtExpiredByPayload(payload)) {
      clearSession();
      return null;
    }

    let flowId =
      typeof data?.flow_id === "string" ? data.flow_id.trim().toLowerCase() : "";
    const participantRaw = data?.participant_id;
    let participantId =
      typeof participantRaw === "string"
        ? participantRaw.trim().toLowerCase()
        : participantRaw != null
          ? String(participantRaw).trim().toLowerCase()
          : "";

    if (payload) {
      const jf = claimString(payload, "flow_id");
      const jp = claimString(payload, "participant_id");
      if (jf) flowId = jf;
      if (jp) participantId = jp;
    }

    if (!flowId || !participantId) {
      return null;
    }

    let role = data.role;
    if (
      payload &&
      (payload.role === "teacher" || payload.role === "student")
    ) {
      role = payload.role;
    }

    const merged: WebClientSession = {
      ...data,
      access_token: token,
      flow_id: flowId,
      participant_id: participantId,
      role,
    };

    if (JSON.stringify(merged) !== raw) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    }

    return merged;
  } catch {
    /* ignore */
  }
  return null;
}

export function saveSession(
  api: WebSessionCreateResponse,
  flowId: string,
): WebClientSession {
  const fid = flowId.trim().toLowerCase();
  const session: WebClientSession = { ...api, flow_id: fid };
  if (isBrowser()) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }
  return session;
}

export function clearSession(): void {
  if (isBrowser()) {
    window.localStorage.removeItem(STORAGE_KEY);
  }
}
