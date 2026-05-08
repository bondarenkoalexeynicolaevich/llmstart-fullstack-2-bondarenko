"""Курсорные ленты: вопросы и сдачи по потоку."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import and_, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.errors import ApiError
from backend.models.assignment import Assignment
from backend.models.lesson import Lesson
from backend.models.material import Material
from backend.models.module import Module
from backend.models.participant import Participant
from backend.models.submission import Submission
from backend.models.user import User
from backend.services.cursor_page import CursorDecodeError, decode_cursor, encode_cursor


async def question_feed_page(
    session: AsyncSession,
    flow_id: uuid.UUID,
    limit: int,
    cursor: str | None,
) -> tuple[list[dict[str, Any]], str | None]:
    bind: dict[str, Any] = {"fid": str(flow_id), "lim": limit + 1}
    cursor_sql = ""
    if cursor:
        try:
            c_dt, c_id = decode_cursor(cursor)
        except CursorDecodeError as exc:
            raise ApiError(
                400,
                "validation_error",
                "Invalid cursor",
            ) from exc
        cursor_sql = (
            " AND (um.asked_at, um.um_id) < (:c_ts::timestamptz, :c_id::uuid)"
        )
        bind["c_ts"] = c_dt.isoformat()
        bind["c_id"] = str(c_id)

    sql = text(
        """
        WITH um AS (
          SELECT dm.id AS um_id, dm.participant_id, dm.content AS qtext,
                 dm.created_at AS asked_at
          FROM dialog_messages dm
          JOIN participants p ON p.id = dm.participant_id
          WHERE p.flow_id = CAST(:fid AS uuid)
            AND p.role::text = 'student'
            AND dm.role::text = 'user'
        )
        SELECT
          um.um_id,
          um.participant_id,
          u.name AS participant_name,
          um.asked_at,
          um.qtext AS question_text,
          (SELECT a.content FROM dialog_messages a
           WHERE a.participant_id = um.participant_id
             AND a.role::text = 'assistant'
             AND a.created_at > um.asked_at
           ORDER BY a.created_at ASC
           LIMIT 1) AS answer_summary
        FROM um
        JOIN participants p2 ON p2.id = um.participant_id
        JOIN users u ON u.id = p2.user_id
        WHERE TRUE
        """
        + cursor_sql
        + """
        ORDER BY um.asked_at DESC, um.um_id DESC
        LIMIT :lim
        """,
    )
    rows_raw = list((await session.execute(sql, bind)).mappings().all())
    page = rows_raw[:limit]
    next_cursor: str | None = None
    if len(rows_raw) > limit:
        last = rows_raw[limit - 1]
        next_cursor = encode_cursor(last["asked_at"], uuid.UUID(str(last["um_id"])))

    items = []
    for r in page:
        items.append(
            {
                "participant_id": uuid.UUID(str(r["participant_id"])),
                "participant_name": str(r["participant_name"]),
                "asked_at": r["asked_at"],
                "question_text": str(r["question_text"]),
                "answer_summary": r["answer_summary"],
            },
        )
    return items, next_cursor


def _material_to_ref(m: Material) -> dict[str, Any]:
    return {
        "id": m.id,
        "title": m.title,
        "type": m.type.value,
        "url": m.url,
        "content": m.content,
    }


async def submission_feed_page(
    session: AsyncSession,
    flow_id: uuid.UUID,
    limit: int,
    cursor: str | None,
) -> tuple[list[dict[str, Any]], str | None]:
    q = (
        select(Submission, User.name, Lesson.id, Lesson.title, Assignment.id, Assignment.title)
        .join(Participant, Participant.id == Submission.participant_id)
        .join(User, User.id == Participant.user_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(Lesson, Lesson.id == Assignment.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.flow_id == flow_id)
    )
    if cursor:
        try:
            c_ts, c_id = decode_cursor(cursor)
        except CursorDecodeError as exc:
            raise ApiError(
                400,
                "validation_error",
                "Invalid cursor",
            ) from exc
        q = q.where(
            or_(
                Submission.submitted_at < c_ts,
                and_(Submission.submitted_at == c_ts, Submission.id < c_id),
            ),
        )
    q = q.order_by(
        Submission.submitted_at.desc(),
        Submission.id.desc(),
    ).limit(limit + 1)

    rows_all = list((await session.execute(q)).all())
    page_rows = rows_all[:limit]
    next_cursor = None
    if len(rows_all) > limit:
        last_row = rows_all[limit - 1]
        sub_last = last_row[0]
        next_cursor = encode_cursor(sub_last.submitted_at, sub_last.id)

    lesson_ids = {r[2] for r in page_rows}
    mats_map: dict[uuid.UUID, list[Material]] = {lid: [] for lid in lesson_ids}
    if lesson_ids:
        m_stmt = select(Material).where(Material.lesson_id.in_(lesson_ids))
        for m in (await session.execute(m_stmt)).scalars():
            mats_map.setdefault(m.lesson_id, []).append(m)

    items = []
    for sub, pname, lid, ltitle, aid, atitle in page_rows:
        materials = [_material_to_ref(m) for m in mats_map.get(lid, [])]
        items.append(
            {
                "submission_id": sub.id,
                "participant_id": sub.participant_id,
                "participant_name": pname,
                "lesson_id": lid,
                "lesson_title": ltitle,
                "assignment_id": aid,
                "assignment_title": atitle,
                "status": sub.status.value,
                "submitted_at": sub.submitted_at,
                "comment": sub.comment,
                "materials": materials,
            },
        )

    return items, next_cursor
