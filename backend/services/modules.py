"""Чтение структуры потока: модули и занятия."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.flow import Flow
from backend.models.module import Module


class FlowNotFoundError(Exception):
    """Поток по flow_id не найден."""

    def __init__(self) -> None:
        super().__init__("flow_not_found")


async def modules_with_lessons_for_flow(
    session: AsyncSession,
    flow_id: uuid.UUID,
) -> list[Module]:
    """Возвращает модули с уроками, если поток существует."""
    exists = await session.get(Flow, flow_id)
    if exists is None:
        raise FlowNotFoundError()
    return await get_modules_with_lessons(session, flow_id)


async def get_modules_with_lessons(
    session: AsyncSession,
    flow_id: uuid.UUID,
) -> list[Module]:
    stmt = (
        select(Module)
        .where(Module.flow_id == flow_id)
        .options(selectinload(Module.lessons))
        .order_by(Module.order)
    )
    result = await session.execute(stmt)
    modules = list(result.scalars().unique().all())
    for m in modules:
        m.lessons.sort(key=lambda le: le.order)
    return modules
