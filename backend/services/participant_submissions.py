"""Список сдач участника."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.participant import Participant
from backend.models.submission import Submission


async def list_submissions_for_participant(
    session: AsyncSession,
    participant_id: uuid.UUID,
) -> list[Submission] | None:
    part = (
        await session.execute(
            select(Participant).where(Participant.id == participant_id)
        )
    ).scalar_one_or_none()
    if part is None:
        return None

    stmt = (
        select(Submission)
        .where(Submission.participant_id == participant_id)
        .order_by(Submission.submitted_at.desc())
    )
    rows = (await session.execute(stmt)).scalars().all()
    return list(rows)
