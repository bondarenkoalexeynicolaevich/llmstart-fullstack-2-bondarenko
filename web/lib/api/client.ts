import { errorMessageFromResponse } from "@/lib/api/http-error";
import { getPublicBackendBaseUrl } from "@/lib/env";
import { clearSession, getSession } from "@/lib/session";

/**
 * Авторизованный GET/POST к backend. При 401 очищает сессию и редирект на /login.
 */
export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const session = getSession();
  if (!session?.access_token) {
    clearSession();
    if (typeof window !== "undefined") {
      window.location.replace(new URL("/login", window.location.origin).href);
    }
    throw new Error("Нет сессии");
  }

  const base = getPublicBackendBaseUrl();
  const url = path.startsWith("http") ? path : `${base}${path}`;

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${session.access_token}`);
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  let res: Response;
  try {
    res = await fetch(url, { ...init, headers });
  } catch (e) {
    const hint =
      "Не удалось достучаться до API. Проверьте backend и NEXT_PUBLIC_BACKEND_BASE_URL.";
    if (e instanceof TypeError) {
      throw new Error(`${hint} (${e.message})`);
    }
    throw e;
  }

  if (res.status === 401) {
    clearSession();
    window.location.replace(new URL("/login", window.location.origin).href);
    throw new Error("Сессия недействительна или истекла");
  }

  if (!res.ok) {
    const msg = await errorMessageFromResponse(res);
    if (res.status === 404 && res.url) {
      throw new Error(`${msg} Запрос: ${res.url}`);
    }
    throw new Error(msg);
  }

  return (await res.json()) as T;
}

/** POST multipart (FormData): не задаёт Content-Type — границу задаёт браузер. */
export async function apiFetchMultipart<T>(
  path: string,
  formData: FormData,
): Promise<T> {
  const session = getSession();
  if (!session?.access_token) {
    clearSession();
    if (typeof window !== "undefined") {
      window.location.replace(new URL("/login", window.location.origin).href);
    }
    throw new Error("Нет сессии");
  }

  const base = getPublicBackendBaseUrl();
  const url = path.startsWith("http") ? path : `${base}${path}`;

  const headers = new Headers();
  headers.set("Authorization", `Bearer ${session.access_token}`);
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  let res: Response;
  try {
    res = await fetch(url, {
      method: "POST",
      body: formData,
      headers,
    });
  } catch (e) {
    const hint =
      "Не удалось достучаться до API. Проверьте backend и NEXT_PUBLIC_BACKEND_BASE_URL.";
    if (e instanceof TypeError) {
      throw new Error(`${hint} (${e.message})`);
    }
    throw e;
  }

  if (res.status === 401) {
    clearSession();
    window.location.replace(new URL("/login", window.location.origin).href);
    throw new Error("Сессия недействительна или истекла");
  }

  if (!res.ok) {
    const msg = await errorMessageFromResponse(res);
    if (res.status === 404 && res.url) {
      throw new Error(`${msg} Запрос: ${res.url}`);
    }
    throw new Error(msg);
  }

  return (await res.json()) as T;
}
