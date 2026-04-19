"""Чтение структуры потока: модули и занятия."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.module import Module


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
