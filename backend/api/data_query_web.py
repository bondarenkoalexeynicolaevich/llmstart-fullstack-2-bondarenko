"""Вопрос преподавателя к агрегированным данным потока (ADR-005)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_web import DataQueryRequestBody, DataQueryResponseOut
from backend.api.web_auth import require_teacher_in_flow
from backend.models.flow import Flow
from backend.services.data_query import run_flow_data_query
from backend.services.llm import LlmClient, get_llm_client
from backend.services.web_jwt import JwtPrincipal

router = APIRouter(tags=["flows"])


async def _flow_or_404(session: AsyncSession, flow_id: uuid.UUID) -> None:
    exists = await session.get(Flow, flow_id)
    if exists is None:
        raise ApiError(404, "flow_not_found", "Flow not found")


@router.post(
    "/flows/{flow_id}/data-query",
    response_model=DataQueryResponseOut,
    summary="Вопрос к данным потока",
)
async def post_flow_data_query(
    flow_id: uuid.UUID,
    body: DataQueryRequestBody,
    session: SessionDep,
    llm: Annotated[LlmClient, Depends(get_llm_client)],
    _principal: Annotated[JwtPrincipal, Depends(require_teacher_in_flow)],
) -> DataQueryResponseOut:
    await _flow_or_404(session, flow_id)
    correlation_id = uuid.uuid4()
    payload = await run_flow_data_query(
        session,
        flow_id,
        body.question,
        llm,
        correlation_id,
    )
    return DataQueryResponseOut.model_validate(payload)
