"""Потоковые GET для веб-клиента (JWT, роль teacher где нужно)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.api.deps import SessionDep
from backend.api.errors import ApiError
from backend.api.schemas_web import (
    ActivityDayOut,
    DashboardKpiOut,
    DashboardPeriodOut,
    LeaderboardResponse,
    ProgressMatrixResponse,
    QuestionFeedPageOut,
    QuestionFeedItemOut,
    SubmissionFeedPageOut,
    SubmissionFeedItemOut,
    MaterialRefOut,
    MatrixCellOut,
    MatrixLessonColumnOut,
    MatrixParticipantRowOut,
    TeacherDashboardResponse,
)
from backend.api.web_auth import require_member_in_flow, require_teacher_in_flow
from backend.models.flow import Flow
from backend.services.flow_analytics import (
    build_dashboard,
    leaderboard_payload,
    progress_matrix_payload,
)
from backend.services.flow_feeds import question_feed_page, submission_feed_page
from backend.services.web_jwt import JwtPrincipal

router = APIRouter(tags=["flows"])


async def _flow_or_404(session, flow_id: uuid.UUID) -> None:
    exists = await session.get(Flow, flow_id)
    if exists is None:
        raise ApiError(404, "flow_not_found", "Flow not found")


@router.get(
    "/flows/{flow_id}/dashboard",
    response_model=TeacherDashboardResponse,
    summary="Дашборд преподавателя",
)
async def get_teacher_dashboard(
    flow_id: uuid.UUID,
    session: SessionDep,
    _principal: Annotated[JwtPrincipal, Depends(require_teacher_in_flow)],
) -> TeacherDashboardResponse:
    await _flow_or_404(session, flow_id)
    raw = await build_dashboard(session, flow_id)
    return TeacherDashboardResponse(
        period=DashboardPeriodOut(**raw["period"]),
        kpis=[DashboardKpiOut(**k) for k in raw["kpis"]],
        activity=[ActivityDayOut(**a) for a in raw["activity"]],
    )


@router.get(
    "/flows/{flow_id}/questions",
    response_model=QuestionFeedPageOut,
    summary="Лента вопросов",
)
async def list_flow_questions(
    flow_id: uuid.UUID,
    session: SessionDep,
    _principal: Annotated[JwtPrincipal, Depends(require_teacher_in_flow)],
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> QuestionFeedPageOut:
    await _flow_or_404(session, flow_id)
    items_raw, next_c = await question_feed_page(session, flow_id, limit, cursor)
    items = [
        QuestionFeedItemOut(
            participant_id=i["participant_id"],
            participant_name=i["participant_name"],
            asked_at=i["asked_at"],
            question_text=i["question_text"],
            answer_summary=i["answer_summary"],
        )
        for i in items_raw
    ]
    return QuestionFeedPageOut(items=items, next_cursor=next_c)


@router.get(
    "/flows/{flow_id}/submissions",
    response_model=SubmissionFeedPageOut,
    summary="Лента сдач по потоку",
)
async def list_flow_submission_feed(
    flow_id: uuid.UUID,
    session: SessionDep,
    _principal: Annotated[JwtPrincipal, Depends(require_teacher_in_flow)],
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
) -> SubmissionFeedPageOut:
    await _flow_or_404(session, flow_id)
    items_raw, next_c = await submission_feed_page(session, flow_id, limit, cursor)
    items_out: list[SubmissionFeedItemOut] = []
    for i in items_raw:
        mats = [
            MaterialRefOut(
                id=m["id"],
                title=m["title"],
                type=m["type"],  # type: ignore[arg-type]
                url=m["url"],
                content=m["content"],
            )
            for m in i["materials"]
        ]
        items_out.append(
            SubmissionFeedItemOut(
                submission_id=i["submission_id"],
                participant_id=i["participant_id"],
                participant_name=i["participant_name"],
                lesson_id=i["lesson_id"],
                lesson_title=i["lesson_title"],
                assignment_id=i["assignment_id"],
                assignment_title=i["assignment_title"],
                status=i["status"],  # type: ignore[arg-type]
                submitted_at=i["submitted_at"],
                comment=i["comment"],
                materials=mats,
            ),
        )
    return SubmissionFeedPageOut(items=items_out, next_cursor=next_c)


@router.get(
    "/flows/{flow_id}/progress-matrix",
    response_model=ProgressMatrixResponse,
    summary="Матрица прогресса",
)
async def get_progress_matrix_route(
    flow_id: uuid.UUID,
    session: SessionDep,
    _principal: Annotated[JwtPrincipal, Depends(require_teacher_in_flow)],
) -> ProgressMatrixResponse:
    await _flow_or_404(session, flow_id)
    raw = await progress_matrix_payload(session, flow_id)
    lessons = [
        MatrixLessonColumnOut(
            id=x["id"],
            title=x["title"],
            module_title=x["module_title"],
            module_order=x["module_order"],
            lesson_order=x["lesson_order"],
        )
        for x in raw["lessons"]
    ]
    rows = [
        MatrixParticipantRowOut(
            participant_id=r["participant_id"],
            display_name=r["display_name"],
            cells=[
                MatrixCellOut(
                    status=c["status"],  # type: ignore[arg-type]
                    submitted_at=c["submitted_at"],
                )
                for c in r["cells"]
            ],
        )
        for r in raw["rows"]
    ]
    return ProgressMatrixResponse(lessons=lessons, rows=rows)


@router.get(
    "/flows/{flow_id}/leaderboard",
    response_model=LeaderboardResponse,
    summary="Лидерборд",
)
async def get_leaderboard_route(
    flow_id: uuid.UUID,
    session: SessionDep,
    _principal: Annotated[JwtPrincipal, Depends(require_member_in_flow)],
) -> LeaderboardResponse:
    await _flow_or_404(session, flow_id)
    raw = await leaderboard_payload(session, flow_id)
    return LeaderboardResponse.model_validate(raw)
