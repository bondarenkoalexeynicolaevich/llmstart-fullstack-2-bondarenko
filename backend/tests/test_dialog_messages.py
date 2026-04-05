"""Сценарий сообщения ассистенту (happy-path и 404)."""

from __future__ import annotations

import uuid

from sqlalchemy import create_engine, text

from backend.config import get_settings
from backend.services.llm import get_llm_client
from backend.tests.constants import TEST_TOKEN
from backend.tests.conftest import (
    _sync_database_url,
    seed_flow_user_participant,
)


class _FakeLlm:
    async def generate_reply(
        self,
        *,
        system_prompt: str,
        messages: list[tuple[str, str]],
    ) -> str:
        _ = system_prompt
        _ = messages
        return "fake-assistant-reply"


def test_dialog_messages_happy_path(app, client):
    app.dependency_overrides[get_llm_client] = lambda: _FakeLlm()
    flow_id, telegram_id, participant_id = seed_flow_user_participant()

    response = client.post(
        "/v1/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": telegram_id,
            "content": "  pinned  ",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reply_text"] == "fake-assistant-reply"
    assert uuid.UUID(payload["user_message_id"])
    assert uuid.UUID(payload["assistant_message_id"])

    settings = get_settings()
    eng = create_engine(_sync_database_url(settings.database_url), pool_pre_ping=True)
    try:
        with eng.connect() as conn:
            count = conn.execute(
                text(
                    "SELECT COUNT(*) FROM dialog_messages WHERE participant_id = :pid",
                ),
                {"pid": participant_id},
            ).scalar()
    finally:
        eng.dispose()
    assert count == 2


def test_dialog_messages_flow_not_found(app, client):
    app.dependency_overrides[get_llm_client] = lambda: _FakeLlm()
    missing_flow = uuid.uuid4()

    response = client.post(
        "/v1/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(missing_flow),
            "telegram_user_id": 1,
            "content": "a",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "flow_not_found"


def test_dialog_messages_participant_not_found(app, client):
    app.dependency_overrides[get_llm_client] = lambda: _FakeLlm()
    flow_id, _, _ = seed_flow_user_participant(telegram_id=100)

    response = client.post(
        "/v1/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": 999_000_999,
            "content": "b",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "participant_not_found"
