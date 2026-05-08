#!/usr/bin/env python3
"""Наполнение БД из data/progress-import.v1.json (async SQLAlchemy).

Требуется DATABASE_URL в .env корня репозитория и применённые миграции (make migrate-upgrade).

Использование из корня:
  make db-seed
  make db-seed-frontend-demo  # то же самое (алиас под frontend tasklist)

После вставки из JSON выполняется idempotent-патч пользователя-демопреподавателя:
telegram_id=459032551 (@Bondarenko_Alexey_Nikolaevich).

Опциональный ключ `dialog_messages`: id, participant_id, role (user|assistant), content, created_at.

Использование напрямую:
  .venv\\Scripts\\python.exe scripts\\seed_data.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from dotenv import load_dotenv
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert

REPO_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _uuid(value: str) -> UUID:
    return UUID(value)


def _load_payload() -> dict[str, Any]:
    path = REPO_ROOT / "data" / "progress-import.v1.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        msg = "Ожидался объект JSON в корне файла"
        raise TypeError(msg)
    return data


async def _seed() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    load_dotenv(REPO_ROOT / ".env")

    from backend.config import get_settings
    from backend.database import dispose_database, init_database, session_scope
    from backend.models.assignment import Assignment
    from backend.models.dialog_message import DialogMessage
    from backend.models.enums import DialogMessageRole
    from backend.models.flow import Flow
    from backend.models.knowledge_item import KnowledgeItem
    from backend.models.lesson import Lesson
    from backend.models.material import Material
    from backend.models.module import Module
    from backend.models.participant import Participant
    from backend.models.submission import Submission
    from backend.models.user import User

    settings = get_settings()
    init_database(settings.database_url)

    payload = _load_payload()
    flows = payload["flows"]
    users = payload["users"]
    modules = payload.get("modules", [])
    lessons = payload.get("lessons", [])
    materials = payload.get("materials", [])
    participants = payload["participants"]
    assignments = payload["assignments"]
    submissions = payload["submissions"]
    knowledge_items = payload.get("knowledge_items", [])
    dialog_messages = payload.get("dialog_messages", [])

    total_attempted = 0

    try:
        async with session_scope() as session:
            for row in flows:
                stmt = (
                    insert(Flow.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        title=row["title"],
                        system_prompt=row["system_prompt"],
                        started_at=date.fromisoformat(row["started_at"]),
                        finished_at=date.fromisoformat(row["finished_at"])
                        if row.get("finished_at")
                        else None,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in users:
                stmt = (
                    insert(User.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        telegram_id=row.get("telegram_id"),
                        telegram_username=row.get("telegram_username"),
                        name=row["name"],
                        email=row.get("email"),
                        role=row["role"],
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in modules:
                stmt = (
                    insert(Module.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        flow_id=_uuid(row["flow_id"]),
                        title=row["title"],
                        order=row["order"],
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in lessons:
                sched: datetime | None = None
                if raw_s := row.get("scheduled_at"):
                    sched = datetime.fromisoformat(raw_s)
                stmt = (
                    insert(Lesson.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        module_id=_uuid(row["module_id"]),
                        title=row["title"],
                        order=row["order"],
                        scheduled_at=sched,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in materials:
                stmt = (
                    insert(Material.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        lesson_id=_uuid(row["lesson_id"]),
                        title=row["title"],
                        type=row["type"],
                        url=row.get("url"),
                        content=row.get("content"),
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in participants:
                stmt = (
                    insert(Participant.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        user_id=_uuid(row["user_id"]),
                        flow_id=_uuid(row["flow_id"]),
                        role=row["role"],
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in dialog_messages:
                created_dm = datetime.fromisoformat(row["created_at"])
                stmt = (
                    insert(DialogMessage.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        participant_id=_uuid(row["participant_id"]),
                        role=DialogMessageRole(row["role"]),
                        content=row["content"],
                        created_at=created_dm,
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in assignments:
                stmt = (
                    insert(Assignment.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        lesson_id=_uuid(row["lesson_id"]),
                        title=row["title"],
                        description=row.get("description"),
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in submissions:
                submitted_at: datetime | None = None
                if raw_ts := row.get("submitted_at"):
                    submitted_at = datetime.fromisoformat(raw_ts)
                values: dict[str, Any] = {
                    "id": _uuid(row["id"]),
                    "assignment_id": _uuid(row["assignment_id"]),
                    "participant_id": _uuid(row["participant_id"]),
                    "status": row["status"],
                    "comment": row.get("comment"),
                }
                if submitted_at is not None:
                    values["submitted_at"] = submitted_at
                stmt = (
                    insert(Submission.__table__)
                    .values(**values)
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            for row in knowledge_items:
                stmt = (
                    insert(KnowledgeItem.__table__)
                    .values(
                        id=_uuid(row["id"]),
                        flow_id=_uuid(row["flow_id"]),
                        content=row["content"],
                        source_url=row.get("source_url"),
                    )
                    .on_conflict_do_nothing(index_elements=["id"])
                )
                await session.execute(stmt)
                total_attempted += 1

            # Демо-преподаватель frontend: telegram_id=459032551 (@Bondarenko_Alexey_Nikolaevich).
            demo_teacher_id = UUID("00000000-0000-0000-0000-000000000021")
            await session.execute(
                update(User.__table__)
                .where(User.__table__.c.id == demo_teacher_id)
                .values(
                    telegram_id=459032551,
                    telegram_username="bondarenko_alexey_nikolaevich",
                    name="Алексей Бондаренко",
                ),
            )

            await session.commit()
    finally:
        await dispose_database()

    logger.info(
        "Seed завершён: обработано вставок (с учётом ON CONFLICT) — %s строк из файла",
        total_attempted,
    )


def main() -> int:
    try:
        asyncio.run(_seed())
    except Exception:
        logger.exception("Ошибка seed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
