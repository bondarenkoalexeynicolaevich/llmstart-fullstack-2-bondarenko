"""Сценарий «сообщение в диалог»: история, запись user/assistant, вызов LLM."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.dialog_message import DialogMessage
from backend.models.enums import DialogMessageRole
from backend.services.llm import LlmClient
from backend.services.participants import resolve_flow_participant


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
