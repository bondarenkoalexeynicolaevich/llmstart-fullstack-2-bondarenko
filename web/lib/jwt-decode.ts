/**
 * Декодирование payload JWT без проверки подписи (только чтение claims).
 * Подпись проверяется на backend при каждом запросе.
 */

function base64UrlDecodeToString(base64Url: string): string {
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const pad = base64.length % 4;
  const padded = pad ? base64 + "=".repeat(4 - pad) : base64;
  if (typeof atob === "undefined") {
    return "";
  }
  return atob(padded);
}

export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) {
      return null;
    }
    const raw = parts[1];
    if (!raw) {
      return null;
    }
    const json = base64UrlDecodeToString(raw);
    if (!json) {
      return null;
    }
    return JSON.parse(json) as Record<string, unknown>;
  } catch {
    return null;
  }
}

/** true если exp в прошлом (секунды Unix). */
export function isJwtExpiredByPayload(payload: Record<string, unknown>): boolean {
  const exp = payload.exp;
  if (typeof exp !== "number") {
    return false;
  }
  return exp * 1000 <= Date.now();
}

export function claimString(payload: Record<string, unknown>, key: string): string {
  const v = payload[key];
  if (typeof v !== "string" || !v.trim()) {
    return "";
  }
  return v.trim().toLowerCase();
}
