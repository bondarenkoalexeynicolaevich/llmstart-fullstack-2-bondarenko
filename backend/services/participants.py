"""Резолв участника потока по telegram_user_id и flow_id."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.flow import Flow
from backend.models.participant import Participant
from backend.models.user import User


class ParticipantResolveError(Exception):
    """Маппится в ApiError на HTTP-слое."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def resolve_flow_participant(
    session: AsyncSession,
    *,
    flow_id: uuid.UUID,
    telegram_user_id: int,
) -> tuple[Flow, Participant]:
    flow_row = (
        await session.execute(select(Flow).where(Flow.id == flow_id))
    ).scalar_one_or_none()
    if flow_row is None:
        raise ParticipantResolveError(404, "flow_not_found", "Flow not found")

    user_row = (
        await session.execute(
            select(User).where(User.telegram_id == telegram_user_id),
        )
    ).scalar_one_or_none()
    if user_row is None:
        raise ParticipantResolveError(
            404,
            "participant_not_found",
            "User is not a participant of this flow",
        )

    participant = (
        await session.execute(
            select(Participant).where(
                Participant.user_id == user_row.id,
                Participant.flow_id == flow_row.id,
            ),
        )
    ).scalar_one_or_none()
    if participant is None:
        raise ParticipantResolveError(
            404,
            "participant_not_found",
            "User is not a participant of this flow",
        )
    return flow_row, participant
