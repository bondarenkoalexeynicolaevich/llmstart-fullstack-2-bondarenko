"""Аутентификация Bearer для /v1/dialog-messages."""

from __future__ import annotations

import uuid

from backend.tests.constants import TEST_TOKEN


def _valid_body(flow_id: uuid.UUID) -> dict:
    return {
        "flow_id": str(flow_id),
        "telegram_user_id": 1,
        "content": "x",
    }


def test_dialog_messages_missing_bearer_returns_401(client):
    response = client.post(
        "/v1/dialog-messages",
        json=_valid_body(uuid.uuid4()),
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "unauthorized"


def test_dialog_messages_wrong_bearer_returns_401(client):
    response = client.post(
        "/v1/dialog-messages",
        headers={"Authorization": "Bearer not-the-token"},
        json=_valid_body(uuid.uuid4()),
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_dialog_messages_valid_bearer_returns_404_when_flow_missing(client):
    # Произвольный flow_id: в БД нет строки — ожидаем не 401, а резолв потока.
    response = client.post(
        "/v1/dialog-messages",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json=_valid_body(uuid.uuid4()),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "flow_not_found"
