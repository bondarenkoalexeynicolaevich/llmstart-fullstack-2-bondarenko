"""GET /v1/flows/{flow_id}/modules."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_modules import LessonRead, ModuleRead
from backend.api.security import require_internal_token
from backend.models.flow import Flow
from backend.services.modules import get_modules_with_lessons

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
    flow = (
        await session.execute(select(Flow).where(Flow.id == flow_id))
    ).scalar_one_or_none()
    if flow is None:
        raise ApiError(404, "flow_not_found", "Flow not found")

    modules = await get_modules_with_lessons(session, flow_id)
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
