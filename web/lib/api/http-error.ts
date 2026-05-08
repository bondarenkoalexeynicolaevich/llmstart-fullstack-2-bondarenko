/** Текст ошибки из JSON ответа backend (envelope) или FastAPI (`detail`). */

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          const m = (item as { msg?: unknown }).msg;
          return typeof m === "string" ? m : JSON.stringify(item);
        }
        return JSON.stringify(item);
      })
      .filter(Boolean);
    if (parts.length) return parts.join("; ");
  }
  return JSON.stringify(detail);
}

export function errorTextFromJsonBody(
  res: Response,
  body: unknown,
): string | null {
  if (
    body &&
    typeof body === "object" &&
    "error" in body &&
    body.error &&
    typeof body.error === "object"
  ) {
    const err = body.error as { message?: unknown; code?: unknown };
    const msg = typeof err.message === "string" ? err.message : "";
    const code = typeof err.code === "string" ? err.code : "";
    if (msg && code) return `${msg} (${code})`;
    if (msg) return msg;
    if (code) return code;
  }
  if (body && typeof body === "object" && "detail" in body) {
    return `${formatDetail((body as { detail: unknown }).detail)} (HTTP ${res.status})`;
  }
  return null;
}

export async function errorMessageFromResponse(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json();
    const formatted = errorTextFromJsonBody(res, body);
    if (formatted) return formatted;
  } catch {
    /* ignore */
  }
  return `Ошибка ${res.status}`;
}
