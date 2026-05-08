"""Голосовой диалог: multipart, STT (mock), тот же сценарий что текст."""

from __future__ import annotations

import uuid

from backend.config import get_settings
from backend.services.llm import get_llm_client
from backend.tests.constants import TEST_TOKEN
from backend.tests.conftest import (
    seed_flow_teacher_student_for_web,
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
        return "fake-voice-assistant"


async def _fake_transcribe(*_a, **_k):
    return "hello from simulated voice"


def _web_token(client, *, username: str, flow_id) -> str:
    r = client.post(
        "/v1/auth/web-session",
        json={
            "telegram_username": username,
            "flow_id": str(flow_id),
        },
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_voice_internal_missing_telegram_user(app, client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-sk")
    get_settings.cache_clear()
    monkeypatch.setattr("backend.api.voice.transcribe_audio", _fake_transcribe)
    app.dependency_overrides[get_llm_client] = lambda: _FakeLlm()
    flow_id, telegram_id, _ = seed_flow_user_participant()

    r = client.post(
        "/v1/voice/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        files={"audio": ("x.webm", b"fake-audio-bytes", "audio/webm")},
        data={"flow_id": str(flow_id)},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"
    app.dependency_overrides.clear()


def test_voice_internal_happy_path(app, client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-sk")
    get_settings.cache_clear()
    monkeypatch.setattr("backend.api.voice.transcribe_audio", _fake_transcribe)
    app.dependency_overrides[get_llm_client] = lambda: _FakeLlm()
    flow_id, telegram_id, _ = seed_flow_user_participant()

    r = client.post(
        "/v1/voice/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        files={"audio": ("x.webm", b"fake-audio-bytes", "audio/webm")},
        data={"flow_id": str(flow_id), "telegram_user_id": str(telegram_id)},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["reply_text"] == "fake-voice-assistant"
    assert body["transcription"] == "hello from simulated voice"
    assert uuid.UUID(body["user_message_id"])
    assert uuid.UUID(body["assistant_message_id"])
    app.dependency_overrides.clear()


def test_voice_jwt_rejects_extra_telegram_user(app, client, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-sk")
    get_settings.cache_clear()
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    tok = _web_token(client, username="StudentWeb", flow_id=flow_id)

    r = client.post(
        "/v1/voice/dialog-messages",
        headers={"Authorization": f"Bearer {tok}"},
        files={"audio": ("x.webm", b"bytes", "audio/webm")},
        data={
            "flow_id": str(flow_id),
            "telegram_user_id": "1",
        },
    )
    assert r.status_code == 400


def test_voice_no_openai_key(app, client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()
    flow_id, telegram_id, _ = seed_flow_user_participant()

    r = client.post(
        "/v1/voice/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        files={"audio": ("x.webm", b"bytes", "audio/webm")},
        data={"flow_id": str(flow_id), "telegram_user_id": str(telegram_id)},
    )
    assert r.status_code == 503
    assert r.json()["error"]["code"] == "stt_unavailable"
