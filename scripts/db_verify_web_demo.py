#!/usr/bin/env python3
"""Проверка: демо-данные для веб-входа есть в той БД, что задана DATABASE_URL.

Тот же путь загрузки .env и get_settings(), что у `make db-seed` и `make run-backend`.
Если здесь «OK», а POST /v1/auth/web-session всё равно 404 — сравни вывод с процессом
uvicorn (перезапуск после смены .env, отдельный DATABASE_URL в окружении IDE).

Использование из корня:
  .venv\\Scripts\\python.exe scripts\\db_verify_web_demo.py
  make db-verify-web-demo
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parent.parent
DEMO_FLOW = "00000000-0000-0000-0000-000000000001"
DEMO_USERNAME = "bondarenko_alexey_nikolaevich"


def _summarize_database_url(database_url: str) -> str:
    norm = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    p = urlparse(norm)
    host = p.hostname or "?"
    port = p.port or 5432
    db = (p.path or "/").lstrip("/") or "?"
    user = p.username or "?"
    return f"user={user} host={host} port={port} db={db} (пароль не показывается)"


async def _run() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    load_dotenv(REPO_ROOT / ".env")

    from backend.config import get_settings
    from backend.database import dispose_database, init_database, session_scope

    get_settings.cache_clear()
    settings = get_settings()
    print("DATABASE_URL (сводка):", _summarize_database_url(settings.database_url))
    init_database(settings.database_url)

    try:
        async with session_scope() as session:
            flow = (
                await session.execute(
                    text("SELECT id::text FROM flows WHERE id = CAST(:fid AS uuid)"),
                    {"fid": DEMO_FLOW},
                )
            ).fetchone()
            print(f"flows[{DEMO_FLOW}]:", "есть" if flow else "НЕТ — сид не в этой БД или другой flow_id")

            user_row = (
                await session.execute(
                    text(
                        "SELECT id::text, telegram_username, telegram_id "
                        "FROM users WHERE lower(telegram_username) = lower(:u)"
                    ),
                    {"u": DEMO_USERNAME},
                )
            ).fetchone()
            print(
                f"users[telegram_username~={DEMO_USERNAME}]:",
                f"id={user_row[0]} name={user_row[1]} telegram_id={user_row[2]}"
                if user_row
                else "НЕТ — пользователь не в этой БД (перепроверь сид)",
            )

            part = None
            if user_row and flow:
                part = (
                    await session.execute(
                        text(
                            "SELECT id::text, role::text FROM participants "
                            "WHERE flow_id = CAST(:fid AS uuid) "
                            "AND user_id = CAST(:uid AS uuid)"
                        ),
                        {"fid": DEMO_FLOW, "uid": user_row[0]},
                    )
                ).fetchone()
                print(
                    "participant(user+flow):",
                    f"id={part[0]} role={part[1]}" if part else "НЕТ — user не участник этого потока",
                )
            else:
                print("participant(user+flow): (пропуск — нет user или flow)")

        print("---")
        if flow and user_row and part:
            print("Итог: OK — для этой БД веб-вход по демо-username возможен.")
        elif flow and user_row:
            print("Итог: FAIL — user или flow есть, но связи participant нет.")
        else:
            print("Итог: FAIL — не хватает строк в БД; повтори make migrate-upgrade && make db-seed")
    finally:
        await dispose_database()


def main() -> int:
    try:
        asyncio.run(_run())
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
