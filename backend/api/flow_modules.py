"""GET /v1/flows/{flow_id}/modules."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_modules import LessonRead, ModuleRead
from backend.api.security import require_internal_token
from backend.services.modules import FlowNotFoundError, modules_with_lessons_for_flow

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_internal_token)])


@router.get(
    "/flows/{flow_id}/modules",
    response_model=list[ModuleRead],
    summary="Модули потока с занятиями",
)
async def list_flow_modules(
    flow_id: uuid.UUID,
    session: SessionDep,
) -> list[ModuleRead]:
    try:
        modules = await modules_with_lessons_for_flow(session, flow_id)
    except FlowNotFoundError as exc:
        raise ApiError(404, "flow_not_found", "Flow not found") from exc
    logger.info("flow_modules_listed flow_id=%s count=%s", flow_id, len(modules))
    return [
        ModuleRead(
            id=m.id,
            title=m.title,
            order=m.order,
            lessons=[
                LessonRead(
                    id=le.id,
                    title=le.title,
                    order=le.order,
                    scheduled_at=le.scheduled_at,
                )
                for le in m.lessons
            ],
        )
        for m in modules
    ]
