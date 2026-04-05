"""Маршрут сдачи ДЗ."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, status

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_submissions import SubmissionCreateRequest, SubmissionResponse
from backend.api.security import require_internal_token
from backend.services.participants import ParticipantResolveError
from backend.services.submissions import SubmissionCreateError, create_submission

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_internal_token)])


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Зафиксировать сдачу задания",
)
async def create_submission_route(
    body: SubmissionCreateRequest,
    session: SessionDep,
) -> SubmissionResponse:
    try:
        row = await create_submission(
            session,
            flow_id=body.flow_id,
            telegram_user_id=body.telegram_user_id,
            assignment_id=body.assignment_id,
            comment=body.comment,
        )
    except ParticipantResolveError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc
    except SubmissionCreateError as exc:
        raise ApiError(exc.status_code, exc.code, exc.message) from exc

    logger.info(
        "submission_created flow_id=%s telegram_user_id=%s submission_id=%s",
        body.flow_id,
        body.telegram_user_id,
        row.id,
    )
    return SubmissionResponse(
        id=row.id,
        assignment_id=row.assignment_id,
        participant_id=row.participant_id,
        status=row.status.value,
        submitted_at=row.submitted_at,
        comment=row.comment,
    )
