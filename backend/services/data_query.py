"""Сценарий «вопрос к данным потока»: LLM только классифицирует intent, выполнение — allowlist-SQL."""

from __future__ import annotations

import json
import logging
import re
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import asc, desc, func, select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.errors import ApiError
from backend.models.assignment import Assignment
from backend.models.enums import DialogMessageRole, MemberRole
from backend.models.dialog_message import DialogMessage
from backend.models.lesson import Lesson
from backend.models.module import Module
from backend.models.participant import Participant
from backend.models.submission import Submission
from backend.models.user import User
from backend.services.llm import LlmClient

logger = logging.getLogger(__name__)

MAX_ROWS = 100

INT_SUBMISSIONS_BY_MODULE = "submissions_by_module"
INT_STUDENTS_NO_SUBMISSIONS = "students_no_submissions"
INT_TOP_STUDENTS_BY_SUBMISSIONS = "top_students_by_submissions"
INT_SUBMISSIONS_BY_PERIOD = "submissions_by_period"
INT_QUESTIONS_COUNT_BY_LESSON = "questions_count_by_lesson"
INT_STUDENT_PROGRESS_SUMMARY = "student_progress_summary"
INT_UNIQUE_STUDENTS_COUNT = "unique_students_count"

CLASSIFIER_PROMPT = """You classify a teacher question about ONE learning flow into a structured intent.

Return ONLY a single JSON object. No markdown, no code fences.

Allowed intents and params shapes:
1) submissions_by_module — count homework submissions recorded in modules with this order position in the flow.
   Params: {"module_order": <positive int>}

2) students_no_submissions — list students (role student) who have ZERO submissions.
   Params: {}

3) top_students_by_submissions — students ranked by submission count (descending).
   Params: {"limit": optional int 1–20 default 10}

4) submissions_by_period — recent individual submissions rows (within last N days).
   Params: {"period_days": optional int 1–90 default 7}

5) questions_count_by_lesson — MVP: COUNT of submissions tied to assignments in the lesson identified by module order + lesson order.
   Params: {"module_order": <positive int>, "lesson_order": <positive int>}

6) student_progress_summary — one row summary for a student whose display name SUBSTRING matches.
   Params: {"student_name": <non-empty string fragment>}

7) unique_students_count — how many distinct students (participants with role student) are enrolled in this flow.
   Params: {}

If nothing fits, use {"intent": "unknown", "params": {}}
"""


def _extract_json_fragment(raw: str) -> str:
    text = raw.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _parse_classifier_json(raw: str) -> tuple[str, dict[str, Any]]:
    try:
        data = json.loads(_extract_json_fragment(raw))
    except json.JSONDecodeError as exc:
        raise ApiError(
            400,
            "unrecognized_intent",
            "Classifier did not return valid JSON",
        ) from exc
    if not isinstance(data, dict):
        raise ApiError(400, "unrecognized_intent", "Malformed classifier payload")
    intent_raw = data.get("intent")
    params_raw = data.get("params")
    if not isinstance(intent_raw, str) or not intent_raw.strip():
        raise ApiError(400, "unrecognized_intent", "Missing intent")
    intent = intent_raw.strip().lower().replace("-", "_")
    if params_raw is None:
        params_raw = {}
    if not isinstance(params_raw, dict):
        raise ApiError(400, "unrecognized_intent", "Params must be an object")
    return intent, params_raw


async def classify_intent(llm: LlmClient, question: str) -> tuple[str, dict[str, Any]]:
    reply = await llm.generate_reply(
        system_prompt=CLASSIFIER_PROMPT,
        messages=[("user", question)],
    )
    return _parse_classifier_json(reply)


def _require_unknown_check(intent: str) -> None:
    if intent == "unknown":
        raise ApiError(
            400,
            "unrecognized_intent",
            "Question cannot be mapped to a supported analytical intent",
        )


def _pos_int(raw: Any, _field: str) -> int:
    try:
        n = int(raw)
    except (TypeError, ValueError) as exc:
        msg = "Invalid numeric parameter"
        raise ApiError(400, "validation_error", msg) from exc
    if n < 1:
        msg = "Parameter must be positive"
        raise ApiError(400, "validation_error", msg)
    return n


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return str(value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except ValueError:
            return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return float(value)
    return value


def _serialize_row(mapping: Row[Any] | dict[str, Any]) -> dict[str, Any]:
    d = mapping._mapping if hasattr(mapping, "_mapping") else mapping
    return {k: _serialize_value(v) for k, v in dict(d).items()}


async def exec_submissions_by_module(
    session: AsyncSession,
    flow_id: uuid.UUID,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    mo = _pos_int(params.get("module_order", 0), "module_order")
    stmt = (
        select(func.count(Submission.id))
        .join(Participant, Participant.id == Submission.participant_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(Lesson, Lesson.id == Assignment.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Module.flow_id == flow_id, Module.order == mo)
    )
    n = int((await session.execute(stmt)).scalar_one())
    explanation = f"В потоке зафиксировано записей о сдачах по занятиям модуля с порядком {mo}: {n}."
    return ([{"submission_count": n}], explanation)


async def exec_unique_students_count(
    session: AsyncSession,
    flow_id: uuid.UUID,
    _params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    stmt = select(func.count(Participant.id)).where(
        Participant.flow_id == flow_id,
        Participant.role == MemberRole.student,
    )
    n = int((await session.execute(stmt)).scalar_one())
    explanation = f"Уникальных студентов в потоке (участники с ролью student): {n}."
    return ([{"unique_student_count": n}], explanation)


async def exec_students_no_submissions(
    session: AsyncSession,
    flow_id: uuid.UUID,
    _params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    stmt = (
        select(User.name.label("student_name"))
        .select_from(Participant)
        .join(User, User.id == Participant.user_id)
        .outerjoin(Submission, Submission.participant_id == Participant.id)
        .where(
            Participant.flow_id == flow_id,
            Participant.role == MemberRole.student,
        )
        .group_by(Participant.id, User.name)
        .having(func.count(Submission.id) == 0)
        .order_by(asc(User.name))
        .limit(MAX_ROWS)
    )
    rows = (await session.execute(stmt)).all()
    data = [_serialize_row(r) for r in rows]
    explanation = f"Студентов без единой сдачи по потоку: {len(data)}."
    return (data, explanation)


async def exec_top_students(
    session: AsyncSession,
    flow_id: uuid.UUID,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    raw_limit = params.get("limit", 10)
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError) as exc:
        msg = "Invalid limit"
        raise ApiError(400, "validation_error", msg) from exc
    limit = max(1, min(20, limit))
    cnt = func.count(Submission.id).label("submission_count")
    stmt = (
        select(User.name.label("student_name"), cnt)
        .select_from(Participant)
        .join(User, User.id == Participant.user_id)
        .outerjoin(Submission, Submission.participant_id == Participant.id)
        .where(
            Participant.flow_id == flow_id,
            Participant.role == MemberRole.student,
        )
        .group_by(Participant.id, User.name)
        .order_by(desc(cnt), asc(User.name))
        .limit(limit)
    )
    rows = (await session.execute(stmt)).all()
    data = [_serialize_row(r) for r in rows]
    explanation = f"Топ {len(data)} студентов по числу записей о сдачах."
    return (data, explanation)


async def exec_submissions_by_period(
    session: AsyncSession,
    flow_id: uuid.UUID,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    pd = params.get("period_days", 7)
    try:
        days = int(pd)
    except (TypeError, ValueError) as exc:
        msg = "Invalid period_days"
        raise ApiError(400, "validation_error", msg) from exc
    days = max(1, min(90, days))
    cutoff = datetime.now(UTC) - timedelta(days=days)
    stmt = (
        select(
            User.name.label("student_name"),
            Assignment.title.label("assignment_title"),
            Submission.status,
            Submission.submitted_at.label("submitted_at"),
        )
        .select_from(Submission)
        .join(Participant, Participant.id == Submission.participant_id)
        .join(User, User.id == Participant.user_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .where(Participant.flow_id == flow_id, Submission.submitted_at >= cutoff)
        .order_by(Submission.submitted_at.desc())
        .limit(MAX_ROWS)
    )
    rows = (await session.execute(stmt)).all()
    data = [_serialize_row(r) for r in rows]
    explanation = f"Последние записи о сдачах за последние {days} дн.: показано не более {len(data)} строк."
    return (data, explanation)


async def exec_lesson_question_proxy(
    session: AsyncSession,
    flow_id: uuid.UUID,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    mo = _pos_int(params.get("module_order", 0), "module_order")
    lo = _pos_int(params.get("lesson_order", 0), "lesson_order")
    stmt = (
        select(func.count(Submission.id))
        .join(Participant, Participant.id == Submission.participant_id)
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .join(Lesson, Lesson.id == Assignment.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(
            Module.flow_id == flow_id,
            Module.order == mo,
            Lesson.order == lo,
        )
    )
    n = int((await session.execute(stmt)).scalar_one())
    explanation = f"По занятию модуль {mo}, урок по порядку {lo}: зафиксировано записей о сдачах: {n}."
    rows = [{"module_order": mo, "lesson_order": lo, "submission_count": n}]
    return (rows, explanation)


async def exec_student_summary(
    session: AsyncSession,
    flow_id: uuid.UUID,
    params: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    fragment = params.get("student_name")
    if not isinstance(fragment, str) or not fragment.strip():
        raise ApiError(400, "validation_error", "student_name is required")
    esc = fragment.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{esc}%"
    sub_cnt = func.count(Submission.id).label("submission_count")
    user_msgs = (
        func.count(DialogMessage.id)
        .filter(
            DialogMessage.role == DialogMessageRole.user,
        )
        .label("user_messages_count")
    )
    stmt = (
        select(
            User.name.label("student_name"),
            sub_cnt,
            user_msgs,
        )
        .select_from(Participant)
        .join(User, User.id == Participant.user_id)
        .outerjoin(Submission, Submission.participant_id == Participant.id)
        .outerjoin(DialogMessage, DialogMessage.participant_id == Participant.id)
        .where(
            Participant.flow_id == flow_id,
            Participant.role == MemberRole.student,
            User.name.ilike(pattern, escape="\\"),
        )
        .group_by(Participant.id, User.name)
        .order_by(asc(User.name))
        .limit(MAX_ROWS)
    )
    rows = (await session.execute(stmt)).all()
    if not rows:
        return (
            [],
            "Студенты по такому фрагменту имени не найдены.",
        )
    data = [_serialize_row(r) for r in rows]
    explanation = f"Найдено записей о студентах: {len(data)} (сдачи и сообщения ассистенту — см. таблицу)."
    return (data, explanation)


Handler = Callable[
    [AsyncSession, uuid.UUID, dict[str, Any]],
    Awaitable[tuple[list[dict[str, Any]], str]],
]

_HANDLERS: dict[str, Handler] = {
    INT_SUBMISSIONS_BY_MODULE: exec_submissions_by_module,
    INT_UNIQUE_STUDENTS_COUNT: exec_unique_students_count,
    INT_STUDENTS_NO_SUBMISSIONS: exec_students_no_submissions,
    INT_TOP_STUDENTS_BY_SUBMISSIONS: exec_top_students,
    INT_SUBMISSIONS_BY_PERIOD: exec_submissions_by_period,
    INT_QUESTIONS_COUNT_BY_LESSON: exec_lesson_question_proxy,
    INT_STUDENT_PROGRESS_SUMMARY: exec_student_summary,
}


async def run_flow_data_query(
    session: AsyncSession,
    flow_id: uuid.UUID,
    question: str,
    llm: LlmClient,
    correlation_id: uuid.UUID,
) -> dict[str, Any]:
    intent, params = await classify_intent(llm, question)
    _require_unknown_check(intent)
    handler = _HANDLERS.get(intent)
    if handler is None:
        raise ApiError(
            400,
            "unrecognized_intent",
            "Unsupported intent after classification",
        )
    result, explanation = await handler(session, flow_id, params)
    if len(result) > MAX_ROWS:
        result = result[:MAX_ROWS]
    logger.info(
        "data_query_done correlation_id=%s intent=%s rows=%s",
        correlation_id,
        intent,
        len(result),
    )
    return {
        "intent": intent,
        "params": params,
        "result": result,
        "explanation": explanation,
        "correlation_id": correlation_id,
    }
