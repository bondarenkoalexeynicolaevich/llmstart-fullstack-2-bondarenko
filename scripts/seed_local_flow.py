#!/usr/bin/env python3
"""Создаёт Flow (+ при необходимости User и Participant) для локальной отладки бота.

Читает DATABASE_URL из .env в корне репозитория. Telegram id: переменная SEED_TELEGRAM_ID
или значение по умолчанию.

Использование из корня:
  .venv\\Scripts\\python.exe scripts\\seed_local_flow.py
  $env:SEED_TELEGRAM_ID=123456789; python scripts\\seed_local_flow.py
"""

from __future__ import annotations

import os
import re
import sys
import uuid
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

REPO_ROOT = Path(__file__).resolve().parent.parent


def _sync_url(async_url: str) -> str:
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)


def _update_env_file(env_path: Path, flow_id: uuid.UUID) -> None:
    text = env_path.read_text(encoding="utf-8")
    # Убрать старые строки FLOW_ID (включая комментарии с подсказкой про flow_id).
    lines = [
        ln
        for ln in text.splitlines(keepends=True)
        if not re.match(r"^\s*#.*FLOW_ID", ln, flags=re.IGNORECASE)
        and not re.match(r"^\s*FLOW_ID\s*=", ln)
    ]
    text = "".join(lines).rstrip("\r\n") + f"\nFLOW_ID={flow_id}\n"
    env_path.write_text(text, encoding="utf-8")


def main() -> int:
    sys.path.insert(0, str(REPO_ROOT))
    load_dotenv(REPO_ROOT / ".env")

    raw_url = (os.environ.get("DATABASE_URL") or "").strip()
    if not raw_url:
        print("DATABASE_URL не задан в .env", file=sys.stderr)
        return 1

    telegram_id = int(os.environ.get("SEED_TELEGRAM_ID", "459032551"))
    system_prompt = (os.getenv("SYSTEM_PROMPT") or "").strip() or (
        "Ты — учебный ассистент. Отвечай кратко, ясно и по делу."
    )

    from backend.models.enums import MemberRole
    from backend.models.flow import Flow
    from backend.models.participant import Participant
    from backend.models.user import User

    eng = create_engine(_sync_url(raw_url), pool_pre_ping=True)
    try:
        Session = sessionmaker(bind=eng)
        with Session() as session:
            user = session.execute(
                select(User).where(User.telegram_id == telegram_id),
            ).scalar_one_or_none()
            if user is None:
                user = User(
                    telegram_id=telegram_id,
                    name="Local dev",
                    role=MemberRole.student,
                )
                session.add(user)
                session.flush()

            flow = Flow(
                title="Local dev flow",
                system_prompt=system_prompt,
                started_at=date.today(),
            )
            session.add(flow)
            session.flush()

            existing = session.execute(
                select(Participant).where(
                    Participant.user_id == user.id,
                    Participant.flow_id == flow.id,
                ),
            ).scalar_one_or_none()
            if existing is None:
                session.add(
                    Participant(
                        user_id=user.id,
                        flow_id=flow.id,
                        role=MemberRole.student,
                    ),
                )
            session.commit()
            flow_id = flow.id
    finally:
        eng.dispose()

    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        _update_env_file(env_file, flow_id)
        print(f"FLOW_ID={flow_id} записан в .env")
    else:
        print(f"FLOW_ID={flow_id} (файл .env не найден, добавьте вручную)")

    print(f"telegram_id участника: {telegram_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
