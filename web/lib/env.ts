/**
 * Базовый URL backend для запросов из браузера.
 * Без завершающего `/` и без суффикса `/v1`: пути в клиенте уже вида `/v1/...`,
 * иначе получится `/v1/v1/...` и ответ FastAPI «Not Found (HTTP 404)».
 */
export function getPublicBackendBaseUrl(): string {
  let s = (process.env.NEXT_PUBLIC_BACKEND_BASE_URL ?? "http://127.0.0.1:8000")
    .trim()
    .replace(/\/+$/, "");
  s = s.replace(/\/v1$/i, "").replace(/\/+$/, "");
  return s;
}
