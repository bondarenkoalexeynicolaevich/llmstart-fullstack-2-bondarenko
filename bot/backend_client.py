"""HTTP-клиент к backend API v1 (диалог)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)

# Запрос к LLM может быть долгим; connect отдельно короче.
_TIMEOUT = httpx.Timeout(120.0, connect=15.0)


class BackendRequestError(Exception):
    """Сеть / недоступность сервиса (без HTTP-ответа)."""


class BackendApiError(Exception):
    """Ответ API с кодом ≠ 2xx."""

    def __init__(
        self,
        *,
        status_code: int,
        error_code: str | None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code


def _parse_api_error_payload(body: dict[str, Any]) -> str | None:
    err = body.get("error")
    if isinstance(err, dict):
        raw = err.get("code")
        if isinstance(raw, str) and raw:
            return raw
    return None


class BackendClient:
    """POST /v1/dialog-messages с Bearer-токеном."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        base = settings.backend_base_url.rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=base,
            headers={"Authorization": f"Bearer {settings.internal_api_token}"},
            timeout=_TIMEOUT,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def post_dialog_message(self, telegram_user_id: int, content: str) -> str:
        payload = {
            "flow_id": str(self._settings.flow_id),
            "telegram_user_id": telegram_user_id,
            "content": content,
        }
        try:
            response = await self._http.post("/v1/dialog-messages", json=payload)
        except httpx.RequestError:
            logger.error(
                "event=backend_request_failed user_id=%s",
                telegram_user_id,
            )
            raise BackendRequestError from None

        if response.is_success:
            data = response.json()
            reply = data.get("reply_text")
            if isinstance(reply, str):
                return reply.strip()
            return ""

        error_code: str | None = None
        try:
            body = response.json()
            if isinstance(body, dict):
                error_code = _parse_api_error_payload(body)
        except ValueError:
            pass

        logger.warning(
            "event=backend_http_error user_id=%s http_status=%s error_code=%s",
            telegram_user_id,
            response.status_code,
            error_code or "",
        )
        raise BackendApiError(
            status_code=response.status_code,
            error_code=error_code,
        )
