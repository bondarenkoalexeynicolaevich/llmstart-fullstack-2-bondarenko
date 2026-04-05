"""Сдачи ДЗ: контракт POST /v1/submissions."""

from __future__ import annotations

import uuid

from backend.tests.constants import TEST_TOKEN
from backend.tests.conftest import seed_assignment, seed_flow_user_participant


def test_submissions_happy_path(client):
    flow_id, telegram_id, _ = seed_flow_user_participant()
    assignment_id = seed_assignment(flow_id=flow_id)

    response = client.post(
        "/v1/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": telegram_id,
            "assignment_id": str(assignment_id),
            "comment": "done",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert uuid.UUID(payload["id"])
    assert payload["assignment_id"] == str(assignment_id)
    assert payload["status"] == "submitted"
    assert payload["comment"] == "done"
    assert "submitted_at" in payload


def test_submissions_assignment_not_found(client):
    flow_id, telegram_id, _ = seed_flow_user_participant()
    other_flow_id, _, _ = seed_flow_user_participant(telegram_id=200)
    assignment_id = seed_assignment(flow_id=other_flow_id)

    response = client.post(
        "/v1/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": telegram_id,
            "assignment_id": str(assignment_id),
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "assignment_not_found"


def test_submissions_duplicate_conflict(client):
    flow_id, telegram_id, _ = seed_flow_user_participant()
    assignment_id = seed_assignment(flow_id=flow_id)

    first = client.post(
        "/v1/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": telegram_id,
            "assignment_id": str(assignment_id),
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/v1/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": telegram_id,
            "assignment_id": str(assignment_id),
        },
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "submission_already_exists"
