"""GET /v1/participants/{participant_id}/submissions."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_participant_submissions import ParticipantSubmissionRead
from backend.api.security import require_internal_token
from backend.services.participant_submissions import list_submissions_for_participant

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_internal_token)])


@router.get(
    "/participants/{participant_id}/submissions",
    response_model=list[ParticipantSubmissionRead],
    summary="Сдачи участника",
)
async def list_participant_submissions_route(
    participant_id: uuid.UUID,
    session: SessionDep,
) -> list[ParticipantSubmissionRead]:
    rows = await list_submissions_for_participant(session, participant_id)
    if rows is None:
        raise ApiError(404, "participant_not_found", "Participant not found")

    logger.info(
        "participant_submissions_listed participant_id=%s count=%s",
        participant_id,
        len(rows),
    )
    return [
        ParticipantSubmissionRead(
            id=s.id,
            assignment_id=s.assignment_id,
            status=s.status.value,
            submitted_at=s.submitted_at,
            comment=s.comment,
        )
        for s in rows
    ]
