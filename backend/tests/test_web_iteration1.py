"""Итерация 1 frontend API: web-session, JWT-эндпоинты потока, веб-диалог."""

from __future__ import annotations

from backend.services.llm import get_llm_client
from backend.tests.constants import TEST_TOKEN
from backend.tests.conftest import seed_assignment, seed_flow_teacher_student_for_web


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


def test_web_session_user_not_found(client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    r = client.post(
        "/v1/auth/web-session",
        json={"telegram_username": "NobodyHere", "flow_id": str(flow_id)},
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "user_not_found"


def test_web_session_success(client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    assert isinstance(tok, str)
    assert len(tok) > 20


def test_dashboard_internal_token_forbidden(client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    r = client.get(
        f"/v1/flows/{flow_id}/dashboard",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
    )
    assert r.status_code == 403


def test_dashboard_student_forbidden(client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    tok = _web_token(client, username="StudentWeb", flow_id=flow_id)
    r = client.get(
        f"/v1/flows/{flow_id}/dashboard",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 403


def test_dashboard_teacher_ok(client):
    flow_id, _, student_pid = seed_flow_teacher_student_for_web()
    assignment_id = seed_assignment(flow_id=flow_id)
    client.post(
        "/v1/submissions",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "flow_id": str(flow_id),
            "telegram_user_id": 459032552,
            "assignment_id": str(assignment_id),
        },
    )

    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    r = client.get(
        f"/v1/flows/{flow_id}/dashboard",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert "kpis" in body and len(body["kpis"]) == 4
    assert "activity" in body and len(body["activity"]) == 14


def test_leaderboard_student_ok(client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    tok = _web_token(client, username="StudentWeb", flow_id=flow_id)
    r = client.get(
        f"/v1/flows/{flow_id}/leaderboard",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert r.status_code == 200
    assert "table" in r.json()


class _FakeLlm:
    async def generate_reply(
        self,
        *,
        system_prompt: str,
        messages: list[tuple[str, str]],
    ) -> str:
        _ = system_prompt
        _ = messages
        return "web-fake-reply"


def test_participant_dialog_web_post(app, client):
    flow_id, _, student_pid = seed_flow_teacher_student_for_web()
    tok = _web_token(client, username="StudentWeb", flow_id=flow_id)
    app.dependency_overrides[get_llm_client] = lambda: _FakeLlm()
    r = client.post(
        f"/v1/participants/{student_pid}/dialog-messages?flow_id={flow_id}",
        headers={"Authorization": f"Bearer {tok}"},
        json={"content": "hello web"},
    )
    assert r.status_code == 201
    assert r.headers.get("Location") == (
        f"/v1/participants/{student_pid}/dialog-messages"
    )
    lst = client.get(
        f"/v1/participants/{student_pid}/dialog-messages?flow_id={flow_id}&limit=50",
        headers={"Authorization": f"Bearer {tok}"},
    )
    assert lst.status_code == 200
    assert len(lst.json()["items"]) >= 2
