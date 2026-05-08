"""Сценарий «сообщение в диалог»: история, запись user/assistant, вызов LLM."""

from __future__ import annotations

import uuid

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.dialog_message import DialogMessage
from backend.models.enums import DialogMessageRole
from backend.models.flow import Flow
from backend.models.participant import Participant
from backend.services.cursor_page import CursorDecodeError, decode_cursor
from backend.services.llm import LlmClient
from backend.services.participants import resolve_flow_participant


class DialogWebAccessError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def _record_dialog_core(
    session: AsyncSession,
    *,
    flow: Flow,
    participant: Participant,
    content: str,
    llm: LlmClient,
    max_history_messages: int,
) -> tuple[str, uuid.UUID, uuid.UUID]:
    prior_limit = max(0, max_history_messages - 1)
    history_rows: list[DialogMessage] = []
    if prior_limit > 0:
        prior_result = await session.execute(
            select(DialogMessage)
            .where(DialogMessage.participant_id == participant.id)
            .order_by(DialogMessage.created_at.desc())
            .limit(prior_limit),
        )
        history_rows = list(reversed(prior_result.scalars().all()))

    history_chat: list[tuple[str, str]] = [
        (m.role.value, m.content) for m in history_rows
    ]

    user_msg = DialogMessage(
        participant_id=participant.id,
        role=DialogMessageRole.user,
        content=content,
    )
    session.add(user_msg)
    await session.flush()

    llm_messages = [*history_chat, (DialogMessageRole.user.value, content)]
    try:
        reply_text = await llm.generate_reply(
            system_prompt=flow.system_prompt,
            messages=llm_messages,
        )
    except Exception:
        await session.rollback()
        raise

    assistant_msg = DialogMessage(
        participant_id=participant.id,
        role=DialogMessageRole.assistant,
        content=reply_text,
    )
    session.add(assistant_msg)
    await session.commit()
    return reply_text, user_msg.id, assistant_msg.id


async def record_dialog_exchange(
    session: AsyncSession,
    *,
    flow_id: uuid.UUID,
    telegram_user_id: int,
    content: str,
    llm: LlmClient,
    max_history_messages: int,
) -> tuple[str, uuid.UUID, uuid.UUID]:
    flow, participant = await resolve_flow_participant(
        session,
        flow_id=flow_id,
        telegram_user_id=telegram_user_id,
    )
    return await _record_dialog_core(
        session,
        flow=flow,
        participant=participant,
        content=content,
        llm=llm,
        max_history_messages=max_history_messages,
    )


async def record_dialog_exchange_for_participant_web(
    session: AsyncSession,
    *,
    flow_id: uuid.UUID,
    participant_id: uuid.UUID,
    content: str,
    llm: LlmClient,
    max_history_messages: int,
) -> tuple[str, uuid.UUID, uuid.UUID]:
    flow = await session.get(Flow, flow_id)
    participant = await session.get(Participant, participant_id)
    if flow is None:
        raise DialogWebAccessError(404, "flow_not_found", "Flow not found")
    if participant is None or participant.flow_id != flow_id:
        raise DialogWebAccessError(
            404,
            "participant_not_found",
            "User is not a participant of this flow",
        )
    return await _record_dialog_core(
        session,
        flow=flow,
        participant=participant,
        content=content,
        llm=llm,
        max_history_messages=max_history_messages,
    )


async def list_dialog_messages_page(
    session: AsyncSession,
    *,
    participant_id: uuid.UUID,
    flow_id: uuid.UUID,
    limit: int,
    cursor: str | None,
) -> tuple[list[DialogMessage], str | None]:
    participant = await session.get(Participant, participant_id)
    if participant is None or participant.flow_id != flow_id:
        raise DialogWebAccessError(
            404,
            "participant_not_found",
            "User is not a participant of this flow",
        )

    q = (
        select(DialogMessage)
        .where(DialogMessage.participant_id == participant_id)
        .order_by(DialogMessage.created_at.asc(), DialogMessage.id.asc())
        .limit(limit + 1)
    )
    if cursor:
        try:
            c_ts, c_id = decode_cursor(cursor)
        except CursorDecodeError as exc:
            from backend.api.errors import ApiError

            raise ApiError(400, "validation_error", "Invalid cursor") from exc
        q = q.where(
            or_(
                DialogMessage.created_at > c_ts,
                and_(
                    DialogMessage.created_at == c_ts,
                    DialogMessage.id > c_id,
                ),
            ),
        )

    rows = list((await session.execute(q)).scalars().all())
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1]
        from backend.services.cursor_page import encode_cursor

        next_cursor = encode_cursor(last.created_at, last.id)
    return page, next_cursor
