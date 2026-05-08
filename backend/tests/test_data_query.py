"""POST /v1/flows/{flow_id}/data-query (итерация 9)."""

from __future__ import annotations

from backend.services.llm import get_llm_client
from backend.tests.constants import TEST_TOKEN
from backend.tests.conftest import seed_assignment, seed_flow_teacher_student_for_web
from backend.tests.test_web_iteration1 import _web_token


def _fake_llm(text: str):
    """Возвращает фабрику «клиента» с фиксированным ответом классификатора."""

    class _Pinned:
        async def generate_reply(
            self,
            *,
            system_prompt: str,
            messages: list[tuple[str, str]],
        ) -> str:
            _ = system_prompt
            _ = messages
            return text

    return _Pinned()


def test_data_query_internal_token_forbidden(client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={"question": "anything"},
    )
    assert r.status_code == 403


def test_data_query_student_forbidden(app, client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    app.dependency_overrides[get_llm_client] = lambda: _fake_llm(
        '{"intent":"students_no_submissions","params":{}}',
    )
    tok = _web_token(client, username="StudentWeb", flow_id=flow_id)
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {tok}"},
        json={"question": "students without homework"},
    )
    assert r.status_code == 403


def test_data_query_unrecognized_intent(app, client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    app.dependency_overrides[get_llm_client] = lambda: _fake_llm(
        '{"intent":"unknown","params":{}}',
    )
    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {tok}"},
        json={"question": "?"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "unrecognized_intent"


def test_data_query_unknown_intent_name(app, client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    app.dependency_overrides[get_llm_client] = lambda: _fake_llm(
        '{"intent":"alien_weapon_stats","params":{}}',
    )
    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {tok}"},
        json={"question": "?"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "unrecognized_intent"


def test_data_query_submissions_by_module_teacher_ok(app, client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
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
    app.dependency_overrides[get_llm_client] = lambda: _fake_llm(
        '{"intent":"submissions_by_module","params":{"module_order":1}}',
    )
    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {tok}"},
        json={"question": "How many submissions in module 1?"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert payload["intent"] == "submissions_by_module"
    assert isinstance(payload["result"], list)
    assert payload["result"][0]["submission_count"] >= 1
    assert "correlation_id" in payload


def test_data_query_unique_students_count(app, client):
    flow_id, _, _ = seed_flow_teacher_student_for_web()
    app.dependency_overrides[get_llm_client] = lambda: _fake_llm(
        '{"intent":"unique_students_count","params":{}}',
    )
    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {tok}"},
        json={"question": "Сколько уникальных студентов?"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "unique_students_count"
    assert body["result"][0]["unique_student_count"] >= 1


def test_data_query_students_no_submissions_structure(app, client):
    """Пустой результат допустим: проверяем контракт 200 после классификатора."""

    flow_id, _, _ = seed_flow_teacher_student_for_web()
    app.dependency_overrides[get_llm_client] = lambda: _fake_llm(
        '{"intent":"students_no_submissions","params":{}}',
    )
    tok = _web_token(client, username="TeacherWeb", flow_id=flow_id)
    r = client.post(
        f"/v1/flows/{flow_id}/data-query",
        headers={"Authorization": f"Bearer {tok}"},
        json={"question": "Who never submitted"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "students_no_submissions"
    assert isinstance(body["result"], list)
