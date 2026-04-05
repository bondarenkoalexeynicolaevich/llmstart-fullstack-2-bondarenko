"""Общие фикстуры API-тестов backend."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from collections.abc import Generator
from datetime import date
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from backend.config import get_settings
from backend.main import create_app
from backend.tests.constants import TEST_TOKEN
from backend.models.assignment import Assignment
from backend.models.enums import MemberRole
from backend.models.flow import Flow
from backend.models.participant import Participant
from backend.models.user import User

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")

pytestmark = pytest.mark.integration


def _sync_database_url(async_url: str) -> str:
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)


def _database_url_for_tests() -> str | None:
    return (os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL") or "").strip() or None


@pytest.fixture(scope="session")
def migrated_database() -> None:
    url = _database_url_for_tests()
    if not url:
        pytest.skip("Set DATABASE_URL or TEST_DATABASE_URL for backend API tests")
    env = {**os.environ, "DATABASE_URL": url}
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            str(REPO_ROOT / "backend" / "alembic.ini"),
            "upgrade",
            "head",
        ],
        check=True,
        cwd=str(REPO_ROOT),
        env=env,
    )


@pytest.fixture(autouse=True)
def _test_env(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    url = _database_url_for_tests()
    if url:
        monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("INTERNAL_API_TOKEN", TEST_TOKEN)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def truncate_core_tables_sync() -> None:
    """Очистка таблиц домена (FK: дочерние → родительские)."""
    settings = get_settings()
    eng = create_engine(_sync_database_url(settings.database_url), pool_pre_ping=True)
    try:
        with eng.begin() as conn:
            conn.execute(
                text(
                    "TRUNCATE TABLE submissions, dialog_messages, assignments, "
                    "participants, users, flows RESTART IDENTITY CASCADE",
                ),
            )
    finally:
        eng.dispose()


@pytest.fixture
def app(migrated_database: None) -> Generator:
    get_settings.cache_clear()
    application = create_app()
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app) -> Generator[TestClient]:
    truncate_core_tables_sync()
    with TestClient(app) as test_client:
        yield test_client
    truncate_core_tables_sync()


def seed_flow_user_participant(
    *,
    telegram_id: int = 42_424_242,
    flow_title: str = "Flow test",
    system_prompt: str = "You are concise.",
) -> tuple[uuid.UUID, int, uuid.UUID]:
    """Вставка User + Flow + Participant синхронно (без общего event loop с async-приложением)."""

    settings = get_settings()
    eng = create_engine(_sync_database_url(settings.database_url), pool_pre_ping=True)
    try:
        SessionLocal = sessionmaker(bind=eng)
        with SessionLocal() as session:
            user = User(
                telegram_id=telegram_id,
                name="Seed user",
                role=MemberRole.student,
            )
            flow = Flow(
                title=flow_title,
                system_prompt=system_prompt,
                started_at=date.today(),
            )
            session.add_all([user, flow])
            session.flush()
            participant = Participant(
                user_id=user.id,
                flow_id=flow.id,
                role=MemberRole.student,
            )
            session.add(participant)
            session.commit()
            flow_id = flow.id
            participant_id = participant.id
    finally:
        eng.dispose()
    return flow_id, telegram_id, participant_id


def seed_assignment(*, flow_id: uuid.UUID, title: str = "Seed assignment") -> uuid.UUID:
    """Задание в том же потоке, что и participant (для тестов сдачи)."""

    settings = get_settings()
    eng = create_engine(_sync_database_url(settings.database_url), pool_pre_ping=True)
    try:
        SessionLocal = sessionmaker(bind=eng)
        with SessionLocal() as session:
            assignment = Assignment(
                flow_id=flow_id,
                title=title,
                description="Test description",
            )
            session.add(assignment)
            session.commit()
            return assignment.id
    finally:
        eng.dispose()
