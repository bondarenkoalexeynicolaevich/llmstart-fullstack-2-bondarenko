"""POST /v1/auth/web-session — выдача JWT по telegram_username + flow_id."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.flow import Flow
from backend.models.participant import Participant
from backend.models.user import User


class WebSessionError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def resolve_user_by_username(
    session: AsyncSession,
    username: str,
) -> User | None:
    normalized = username.strip().lower()
    if not normalized:
        return None
    stmt = select(User).where(
        func.lower(User.telegram_username) == normalized,
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def build_web_session_context(
    session: AsyncSession,
    *,
    telegram_username: str,
    flow_id: uuid.UUID,
) -> tuple[User, Participant]:
    user = await resolve_user_by_username(session, telegram_username)
    if user is None:
        raise WebSessionError(404, "user_not_found", "No user matches this telegram username")

    flow = (
        await session.execute(select(Flow).where(Flow.id == flow_id))
    ).scalar_one_or_none()
    if flow is None:
        raise WebSessionError(404, "flow_not_found", "Flow not found")

    participant = (
        await session.execute(
            select(Participant).where(
                Participant.user_id == user.id,
                Participant.flow_id == flow_id,
            ),
        )
    ).scalar_one_or_none()
    if participant is None:
        raise WebSessionError(
            404,
            "user_not_in_flow",
            "User is not a participant of the given flow",
        )
    return user, participant

