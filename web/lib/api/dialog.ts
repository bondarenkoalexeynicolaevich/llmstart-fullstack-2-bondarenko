import {
  apiFetch,
  apiFetchMultipart,
} from "@/lib/api/client";
import type {
  DialogMessageCreateResponse,
  DialogMessageListPage,
} from "@/lib/api/types";

function dialogBasePath(participantId: string): string {
  const enc = encodeURIComponent(participantId);
  return `/v1/participants/${enc}/dialog-messages`;
}

export async function fetchDialogMessages(
  participantId: string,
  flowId: string,
  limit = 50,
): Promise<DialogMessageListPage> {
  const q = new URLSearchParams();
  q.set("flow_id", flowId);
  q.set("limit", String(limit));
  return apiFetch<DialogMessageListPage>(
    `${dialogBasePath(participantId)}?${q.toString()}`,
  );
}

export async function postDialogMessage(
  participantId: string,
  flowId: string,
  content: string,
): Promise<DialogMessageCreateResponse> {
  const q = new URLSearchParams();
  q.set("flow_id", flowId);
  return apiFetch<DialogMessageCreateResponse>(
    `${dialogBasePath(participantId)}?${q.toString()}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    },
  );
}

export async function postVoiceDialogMessage(
  flowId: string,
  audio: Blob,
  filename: string,
): Promise<DialogMessageCreateResponse> {
  const fd = new FormData();
  fd.append("flow_id", flowId);
  fd.append("audio", audio, filename);
  return apiFetchMultipart<DialogMessageCreateResponse>(
    `/v1/voice/dialog-messages`,
    fd,
  );
}
