"""Интеграция: структура потока (модули) и read сдач после POST /v1/submissions."""

from __future__ import annotations

import uuid

from backend.tests.constants import TEST_TOKEN
from backend.tests.conftest import seed_assignment, seed_flow_user_participant


def test_flow_modules_and_participant_submissions_chain(client) -> None:
    flow_id, telegram_id, participant_id = seed_flow_user_participant()
    assignment_id = seed_assignment(flow_id=flow_id)

    post = client.post(
        "/v1/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": telegram_id,
            "assignment_id": str(assignment_id),
            "comment": "integration",
        },
    )
    assert post.status_code == 201

    mod_resp = client.get(
        f"/v1/flows/{flow_id}/modules",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert mod_resp.status_code == 200
    modules = mod_resp.json()
    assert len(modules) == 1
    assert modules[0]["title"] == "Seed module"
    assert len(modules[0]["lessons"]) == 1
    assert modules[0]["lessons"][0]["title"] == "Seed lesson"

    sub_resp = client.get(
        f"/v1/participants/{participant_id}/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert sub_resp.status_code == 200
    rows = sub_resp.json()
    assert len(rows) == 1
    assert rows[0]["assignment_id"] == str(assignment_id)
    assert rows[0]["status"] == "submitted"
    assert rows[0]["comment"] == "integration"


def test_flow_modules_not_found(client) -> None:
    missing = uuid.uuid4()
    r = client.get(
        f"/v1/flows/{missing}/modules",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "flow_not_found"


def test_participant_submissions_not_found(client) -> None:
    missing = uuid.uuid4()
    r = client.get(
        f"/v1/participants/{missing}/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "participant_not_found"
