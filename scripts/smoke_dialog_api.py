#!/usr/bin/env python3
"""Smoke: POST /v1/dialog-messages против запущенного backend.

Нужны переменные окружения (как в .env):
  BACKEND_BASE_URL, INTERNAL_API_TOKEN, FLOW_ID, TELEGRAM_USER_ID

Пример (PowerShell): $env:TELEGRAM_USER_ID=12345; make smoke-dialog
"""

from __future__ import annotations

import json
import os
import sys
import uuid


def main() -> int:
    base = os.environ.get("BACKEND_BASE_URL", "").strip().rstrip("/")
    token = os.environ.get("INTERNAL_API_TOKEN", "").strip()
    flow_raw = os.environ.get("FLOW_ID", "").strip()
    tg_raw = os.environ.get("TELEGRAM_USER_ID", "").strip()

    if not all((base, token, flow_raw, tg_raw)):
        sys.stderr.write(
            "Задайте BACKEND_BASE_URL, INTERNAL_API_TOKEN, FLOW_ID, TELEGRAM_USER_ID.\n",
        )
        return 2

    try:
        flow_id = uuid.UUID(flow_raw)
        telegram_user_id = int(tg_raw)
    except (TypeError, ValueError):
        sys.stderr.write("FLOW_ID должен быть UUID, TELEGRAM_USER_ID — целое число.\n")
        return 2

    try:
        import httpx
    except ImportError:
        sys.stderr.write("Установите зависимости: make install\n")
        return 2

    url = f"{base}/v1/dialog-messages"
    payload = {
        "flow_id": str(flow_id),
        "telegram_user_id": telegram_user_id,
        "content": "smoke",
    }
    headers = {"Authorization": f"Bearer {token}"}

    with httpx.Client(timeout=120.0) as client:
        r = client.post(url, json=payload, headers=headers)

    out = {"http_status": r.status_code}
    try:
        out["body"] = r.json()
    except ValueError:
        out["body_raw_len"] = len(r.content)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if r.is_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
