"""Создание сдачи задания."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.assignment import Assignment
from backend.models.enums import SubmissionStatus
from backend.models.lesson import Lesson
from backend.models.module import Module
from backend.models.submission import Submission
from backend.services.participants import resolve_flow_participant


class SubmissionCreateError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def create_submission(
    session: AsyncSession,
    *,
    flow_id: uuid.UUID,
    telegram_user_id: int,
    assignment_id: uuid.UUID,
    comment: str | None,
) -> Submission:
    _, participant = await resolve_flow_participant(
        session,
        flow_id=flow_id,
        telegram_user_id=telegram_user_id,
    )
    stmt = (
        select(Assignment)
        .join(Lesson, Assignment.lesson_id == Lesson.id)
        .join(Module, Lesson.module_id == Module.id)
        .where(Assignment.id == assignment_id, Module.flow_id == flow_id)
    )
    assignment = (await session.execute(stmt)).scalar_one_or_none()
    if assignment is None:
        raise SubmissionCreateError(
            404,
            "assignment_not_found",
            "Assignment not found or not in this flow",
        )

    submitted_at = datetime.now(UTC)
    submission = Submission(
        assignment_id=assignment.id,
        participant_id=participant.id,
        status=SubmissionStatus.submitted,
        submitted_at=submitted_at,
        comment=comment,
    )
    session.add(submission)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise SubmissionCreateError(
            409,
            "submission_already_exists",
            "Submission already exists for this assignment and participant",
        ) from None
    return submission
