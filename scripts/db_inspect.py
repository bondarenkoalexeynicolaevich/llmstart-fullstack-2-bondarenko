#!/usr/bin/env python3
"""Сводка COUNT(*) по таблицам домена (после миграций 003+004).

Читает DATABASE_URL из .env в корне репозитория.

Использование из корня:
  .venv\\Scripts\\python.exe scripts\\db_inspect.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

REPO_ROOT = Path(__file__).resolve().parent.parent

TABLES = (
    "users",
    "flows",
    "modules",
    "lessons",
    "materials",
    "participants",
    "assignments",
    "dialog_messages",
    "submissions",
    "knowledge_items",
)


async def _run() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    load_dotenv(REPO_ROOT / ".env")

    from backend.config import get_settings
    from backend.database import dispose_database, init_database, session_scope

    settings = get_settings()
    init_database(settings.database_url)

    try:
        async with session_scope() as session:
            rows: list[tuple[str, int]] = []
            for table in TABLES:
                res = await session.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                count = int(res.scalar_one())
                rows.append((table, count))

        width = max(len(t) for t in TABLES)
        print(f"{'table'.ljust(width)}  count")
        print("-" * (width + 8))
        for name, count in rows:
            print(f"{name.ljust(width)}  {count}")
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
