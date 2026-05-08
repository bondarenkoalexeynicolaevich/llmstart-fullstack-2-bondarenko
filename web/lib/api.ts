import { errorMessageFromResponse } from "@/lib/api/http-error";
import { getPublicBackendBaseUrl } from "@/lib/env";
import type { WebSessionCreateResponse } from "@/lib/types";

export async function createWebSession(payload: {
  telegram_username: string;
  flow_id: string;
}): Promise<WebSessionCreateResponse> {
  const base = getPublicBackendBaseUrl();
  const url = `${base}/v1/auth/web-session`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    const hint =
      "Не удалось достучаться до API. Проверьте: uvicorn запущен, в web/.env.local задан NEXT_PUBLIC_BACKEND_BASE_URL (как в адресе бэкенда), после смены .env перезапустите next dev.";
    if (e instanceof TypeError) {
      throw new Error(`${hint} (${e.message})`);
    }
    throw e;
  }
  if (!res.ok) {
    throw new Error(await errorMessageFromResponse(res));
  }
  return (await res.json()) as WebSessionCreateResponse;
}
