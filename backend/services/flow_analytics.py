"""Агрегаты потока: дашборд преподавателя, ленты, матрица, лидерборд."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import case, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.assignment import Assignment
from backend.models.dialog_message import DialogMessage
from backend.models.enums import DialogMessageRole, MemberRole, SubmissionStatus
from backend.models.lesson import Lesson
from backend.models.module import Module
from backend.models.participant import Participant
from backend.models.submission import Submission
from backend.models.user import User


def _utc_today() -> date:
    return datetime.now(UTC).date()


def dashboard_windows() -> tuple[date, date, date, date]:
    """Текущие 14 дней (последний день = сегодня UTC) и предыдущие 14 полных."""
    end = _utc_today()
    cur_start = end - timedelta(days=13)
    prev_end = cur_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=13)
    return cur_start, end, prev_start, prev_end


def window_bounds(d0: date, d1: date) -> tuple[datetime, datetime]:
    """Как [start_dt, next_after_end_dt) в UTC для полузакрытого интервала по дням календаря."""
    start_dt = datetime(d0.year, d0.month, d0.day, tzinfo=UTC)
    upper = datetime(d1.year, d1.month, d1.day, tzinfo=UTC) + timedelta(days=1)
    return start_dt, upper


async def dashboard_active_students(
    session: AsyncSession,
    flow_id: uuid.UUID,
    window_start_dt: datetime,
    window_end_excl_dt: datetime,
) -> int:
    stmt = (
        select(func.count(distinct(DialogMessage.participant_id)))
        .join(Participant, Participant.id == DialogMessage.participant_id)
        .where(
            Participant.flow_id == flow_id,
            Participant.role == MemberRole.student,
            DialogMessage.role == DialogMessageRole.user,
            DialogMessage.created_at >= window_start_dt,
            DialogMessage.created_at < window_end_excl_dt,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def dashboard_submissions_count(
    session: AsyncSession,
    flow_id: uuid.UUID,
    window_start_dt: datetime,
    window_end_excl_dt: datetime,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Submission)
        .join(Participant, Participant.id == Submission.participant_id)
        .where(
            Participant.flow_id == flow_id,
            Submission.submitted_at >= window_start_dt,
            Submission.submitted_at < window_end_excl_dt,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def dashboard_questions_count(
    session: AsyncSession,
    flow_id: uuid.UUID,
    window_start_dt: datetime,
    window_end_excl_dt: datetime,
) -> int:
    stmt = (
        select(func.count())
        .select_from(DialogMessage)
        .join(Participant, Participant.id == DialogMessage.participant_id)
        .where(
            Participant.flow_id == flow_id,
            Participant.role == MemberRole.student,
            DialogMessage.role == DialogMessageRole.user,
            DialogMessage.created_at >= window_start_dt,
            DialogMessage.created_at < window_end_excl_dt,
        )
    )
    return int((await session.execute(stmt)).scalar_one())


async def count_students_assignments(
    session: AsyncSession,
    flow_id: uuid.UUID,
) -> tuple[int, int]:
    studs = (
        await session.execute(
            select(func.count())
            .select_from(Participant)
            .where(
                Participant.flow_id == flow_id,
                Participant.role == MemberRole.student,
            ),
        )
    ).scalar_one()
    asg = (
        await session.execute(
            select(func.count())
            .select_from(Assignment)
            .join(Lesson, Lesson.id == Assignment.lesson_id)
            .join(Module, Module.id == Lesson.module_id)
            .where(Module.flow_id == flow_id),
        )
    ).scalar_one()
    return int(studs), int(asg)


async def dashboard_completion_rate(
    session: AsyncSession,
    flow_id: uuid.UUID,
    window_start_dt: datetime,
    window_end_excl_dt: datetime,
) -> float:
    studs, asg_count = await count_students_assignments(session, flow_id)
    denom = studs * asg_count
    if denom == 0:
        return 0.0
    approved = (
        await session.execute(
            select(func.count())
            .select_from(Submission)
            .join(Participant, Participant.id == Submission.participant_id)
            .where(
                Participant.flow_id == flow_id,
                Participant.role == MemberRole.student,
                Submission.status == SubmissionStatus.approved,
                Submission.submitted_at >= window_start_dt,
                Submission.submitted_at < window_end_excl_dt,
            ),
        )
    ).scalar_one()
    return round(100.0 * float(approved) / float(denom), 2)


def _kpi_delta_direction(cur: float, prev: float) -> str:
    if cur > prev:
        return "up"
    if cur < prev:
        return "down"
    return "unchanged"


def _dashboard_kpi_row(kid: str, cur: float, prev: float, unit: str) -> dict:
    delta_dir = _kpi_delta_direction(cur, prev)
    delta = round(cur - prev, 4 if unit == "percent" else 2)
    return {
        "id": kid,
        "value": round(cur, 2),
        "delta": delta,
        "delta_direction": delta_dir,
        "unit": unit,
    }


async def build_dashboard(session: AsyncSession, flow_id: uuid.UUID) -> dict:
    c0, c1, p0, p1 = dashboard_windows()
    cur_s, cur_e = window_bounds(c0, c1)
    prv_s, prv_e = window_bounds(p0, p1)

    act_cur = await dashboard_active_students(session, flow_id, cur_s, cur_e)
    act_prev = await dashboard_active_students(session, flow_id, prv_s, prv_e)
    sub_cur = await dashboard_submissions_count(session, flow_id, cur_s, cur_e)
    sub_prev = await dashboard_submissions_count(session, flow_id, prv_s, prv_e)
    q_cur = await dashboard_questions_count(session, flow_id, cur_s, cur_e)
    q_prev = await dashboard_questions_count(session, flow_id, prv_s, prv_e)
    cr_cur = await dashboard_completion_rate(session, flow_id, cur_s, cur_e)
    cr_prev = await dashboard_completion_rate(session, flow_id, prv_s, prv_e)

    kpis = [
        _dashboard_kpi_row("active_students", float(act_cur), float(act_prev), "count"),
        _dashboard_kpi_row("submissions_count", float(sub_cur), float(sub_prev), "count"),
        _dashboard_kpi_row("questions_count", float(q_cur), float(q_prev), "count"),
        _dashboard_kpi_row("completion_rate", cr_cur, cr_prev, "percent"),
    ]

    day_expr = func.date_trunc("day", DialogMessage.created_at).label("d")
    q_act = (
        select(day_expr, func.count().label("cnt"))
        .join(Participant, Participant.id == DialogMessage.participant_id)
        .where(
            Participant.flow_id == flow_id,
            Participant.role == MemberRole.student,
            DialogMessage.role == DialogMessageRole.user,
            DialogMessage.created_at >= cur_s,
            DialogMessage.created_at < cur_e,
        )
        .group_by(day_expr)
    )
    rows = (await session.execute(q_act)).all()
    day_map: dict[date, int] = {}
    for drow, cnt in rows:
        day_map[drow.date()] = int(cnt)

    activity = []
    for i in range(14):
        d = c0 + timedelta(days=i)
        activity.append({"date": d, "count": day_map.get(d, 0)})

    return {
        "period": {
            "start_date": c0,
            "end_date": c1,
            "label": "Last 14 days",
        },
        "kpis": kpis,
        "activity": activity,
    }


async def load_lesson_columns(session: AsyncSession, flow_id: uuid.UUID) -> list[dict]:
    stmt = (
        select(
            Lesson.id,
            Lesson.title,
            Lesson.order,
            Module.title,
            Module.order,
        )
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.flow_id == flow_id)
        .order_by(Module.order, Lesson.order)
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": lid,
            "title": ltitle,
            "lesson_order": lorder,
            "module_title": mtitle,
            "module_order": morder,
        }
        for lid, ltitle, lorder, mtitle, morder in rows
    ]


async def list_student_participants(
    session: AsyncSession,
    flow_id: uuid.UUID,
) -> list[tuple[uuid.UUID, str]]:
    stmt = (
        select(Participant.id, User.name)
        .join(User, User.id == Participant.user_id)
        .where(Participant.flow_id == flow_id, Participant.role == MemberRole.student)
        .order_by(User.name.asc(), Participant.id.asc())
    )
    return list((await session.execute(stmt)).all())


async def progress_matrix_payload(
    session: AsyncSession,
    flow_id: uuid.UUID,
) -> dict:
    lessons = await load_lesson_columns(session, flow_id)
    lesson_ids = [r["id"] for r in lessons]
    students = await list_student_participants(session, flow_id)
    student_ids = [s[0] for s in students]
    cells: dict[tuple[uuid.UUID, uuid.UUID], tuple[str | None, datetime | None]] = {}
    if student_ids and lesson_ids:
        dm = SubmissionStatus
        rank = case(
            (Submission.status == dm.approved, 3),
            (Submission.status == dm.reviewed, 2),
            (Submission.status == dm.submitted, 1),
            else_=0,
        )
        subq = (
            select(
                Submission.participant_id.label("pid"),
                Assignment.lesson_id.label("lid"),
                func.max(rank).label("best"),
                func.max(Submission.submitted_at).label("last_at"),
            )
            .join(Assignment, Assignment.id == Submission.assignment_id)
            .where(
                Submission.participant_id.in_(student_ids),
                Assignment.lesson_id.in_(lesson_ids),
            )
            .group_by(Submission.participant_id, Assignment.lesson_id)
        ).subquery()
        rev = {3: "approved", 2: "reviewed", 1: "submitted"}
        stmt = select(subq.c.pid, subq.c.lid, subq.c.best, subq.c.last_at)
        rows = (await session.execute(stmt)).all()
        for pid, lid, best, lat in rows:
            st = rev.get(int(best)) if best is not None else None
            cells[(pid, lid)] = (st, lat)

    out_rows = []
    for pid, pname in students:
        row_cells = []
        for le in lesson_ids:
            st, submitted_at = cells.get((pid, le), (None, None))
            row_cells.append(
                {
                    "status": st,
                    "submitted_at": submitted_at,
                },
            )
        out_rows.append(
            {
                "participant_id": pid,
                "display_name": pname,
                "cells": row_cells,
            },
        )

    ls_out = []
    for r in lessons:
        ls_out.append(
            {
                "id": r["id"],
                "title": r["title"],
                "module_title": r["module_title"],
                "module_order": r["module_order"],
                "lesson_order": r["lesson_order"],
            },
        )
    return {"lessons": ls_out, "rows": out_rows}


def _overall_progress(approvals: int, denominator_cells: int) -> float:
    if denominator_cells == 0:
        return 0.0
    return float(
        (Decimal(100) * Decimal(approvals) / Decimal(denominator_cells)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        ),
    )


def lesson_state_for_submissions(statuses: list[str | None]) -> str:
    if not statuses:
        return "none"
    if any(x is not None for x in statuses) and any(x is None for x in statuses):
        return "partial"
    if all(x is None for x in statuses):
        return "none"
    if all(x == "approved" for x in statuses):
        return "done"
    return "partial"


STATUS_RANK = {"approved": 3, "reviewed": 2, "submitted": 1}


async def leaderboard_payload(session: AsyncSession, flow_id: uuid.UUID) -> dict:
    lessons_meta = await load_lesson_columns(session, flow_id)
    lesson_ids = [m["id"] for m in lessons_meta]

    studs, asgn_total = await count_students_assignments(session, flow_id)
    denominator = studs * asgn_total if studs and asgn_total else 0

    participants = await list_student_participants(session, flow_id)
    p_ids = [p[0] for p in participants]
    pname = {pid: nm for pid, nm in participants}

    user_msg_counts = {
        pid: cnt
        for pid, cnt in (
            (
                await session.execute(
                    select(DialogMessage.participant_id, func.count())
                    .select_from(DialogMessage)
                    .where(
                        DialogMessage.participant_id.in_(p_ids),
                        DialogMessage.role == DialogMessageRole.user,
                    )
                    .group_by(DialogMessage.participant_id),
                )
            ).all()
        )
    }

    approved_counts: dict[uuid.UUID, int] = {pid: 0 for pid in p_ids}
    if p_ids:
        q = (
            select(Submission.participant_id, func.count())
            .select_from(Submission)
            .where(
                Submission.participant_id.in_(p_ids),
                Submission.status == SubmissionStatus.approved,
            )
            .group_by(Submission.participant_id)
        )
        for pid, c in (await session.execute(q)).all():
            approved_counts[pid] = int(c)

    lesson_assignments_ids: dict[uuid.UUID, list[uuid.UUID]] = {lid: [] for lid in lesson_ids}
    if lesson_ids:
        q_la = (
            select(Assignment.id, Assignment.lesson_id)
            .where(Assignment.lesson_id.in_(lesson_ids))
        )
        for aid, lid in (await session.execute(q_la)).all():
            lesson_assignments_ids.setdefault(lid, []).append(aid)

    status_by_assignment: dict[tuple[uuid.UUID, uuid.UUID], str] = {}
    if p_ids:
        q_stat = (
            select(
                Submission.participant_id,
                Submission.assignment_id,
                Submission.status,
            )
            .select_from(Submission)
            .where(Submission.participant_id.in_(p_ids))
        )
        for pid, aid, st in (await session.execute(q_stat)).all():
            key = (pid, aid)
            name = st.value
            prev = status_by_assignment.get(key)
            if prev is None or STATUS_RANK[name] > STATUS_RANK.get(prev, 0):
                status_by_assignment[key] = name

    table = []
    for pid in p_ids:
        appr = approved_counts.get(pid, 0)
        overall = _overall_progress(appr, denominator) if denominator else 0.0
        lesson_icons = []
        for lid in lesson_ids:
            assigns = lesson_assignments_ids.get(lid, [])
            statuses = [status_by_assignment.get((pid, a)) for a in assigns]
            lesson_icons.append(
                {"lesson_id": lid, "state": lesson_state_for_submissions(statuses)},
            )
        table.append(
            (
                pid,
                pname.get(pid, ""),
                overall,
                lesson_icons,
                int(user_msg_counts.get(pid, 0)),
            ),
        )

    table.sort(key=lambda r: (-r[2], r[0]))

    leaderboard_rows_out = []
    scatter_out = []
    for idx, row in enumerate(table, start=1):
        pid, name, prog, icons, ux = row
        medal = None
        if idx == 1:
            medal = "gold"
        elif idx == 2:
            medal = "silver"
        elif idx == 3:
            medal = "bronze"
        leaderboard_rows_out.append(
            {
                "rank": idx,
                "participant_id": pid,
                "display_name": name,
                "overall_progress": prog,
                "lesson_statuses": icons,
                "medal": medal if idx <= 3 else None,
            },
        )
        scatter_out.append(
            {
                "participant_id": pid,
                "display_name": name,
                "x": float(ux),
                "y": float(prog),
                "rank": idx,
            },
        )

    return {
        "scatter_meta": {
            "axis_x_label": "Сообщений пользователя в чате",
            "axis_y_label": "Общий прогресс, %",
        },
        "table": leaderboard_rows_out,
        "scatter": scatter_out,
    }

