"""Схемы HTTP для веб-клиента (OpenAPI v1)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WebSessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    telegram_username: str = Field(..., min_length=1)
    flow_id: uuid.UUID

    @field_validator("telegram_username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> str:
        if not isinstance(value, str):
            msg = "telegram_username must be a string"
            raise TypeError(msg)
        s = value.strip().lstrip("@")
        if not s:
            msg = "telegram_username must be non-empty after trim"
            raise ValueError(msg)
        return s


class WebSessionCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    user_id: uuid.UUID
    participant_id: uuid.UUID
    role: Literal["student", "teacher"]
    display_name: str


class DashboardKpiOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Literal[
        "active_students",
        "submissions_count",
        "questions_count",
        "completion_rate",
    ]
    value: float
    delta: float
    delta_direction: Literal["up", "down", "unchanged"]
    unit: Literal["count", "percent"]


class ActivityDayOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date
    count: int


class DashboardPeriodOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_date: date
    end_date: date
    label: str


class TeacherDashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period: DashboardPeriodOut
    kpis: list[DashboardKpiOut]
    activity: list[ActivityDayOut]


class CursorPageMixin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    next_cursor: str | None


class QuestionFeedItemOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    participant_id: uuid.UUID
    participant_name: str
    asked_at: datetime
    question_text: str
    answer_summary: str | None = None


class QuestionFeedPageOut(CursorPageMixin):
    items: list[QuestionFeedItemOut]


class MaterialRefOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    title: str
    type: Literal["link", "file", "text"]
    url: str | None = None
    content: str | None = None


class SubmissionFeedItemOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    submission_id: uuid.UUID
    participant_id: uuid.UUID
    participant_name: str
    lesson_id: uuid.UUID
    lesson_title: str
    assignment_id: uuid.UUID
    assignment_title: str
    status: Literal["submitted", "reviewed", "approved"]
    submitted_at: datetime
    comment: str | None = None
    materials: list[MaterialRefOut]


class SubmissionFeedPageOut(CursorPageMixin):
    items: list[SubmissionFeedItemOut]


class MatrixCellOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["submitted", "reviewed", "approved"] | None = None
    submitted_at: datetime | None = None


class MatrixLessonColumnOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    title: str
    module_title: str
    module_order: int
    lesson_order: int


class MatrixParticipantRowOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    participant_id: uuid.UUID
    display_name: str
    cells: list[MatrixCellOut]


class ProgressMatrixResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lessons: list[MatrixLessonColumnOut]
    rows: list[MatrixParticipantRowOut]


class LessonStatusIconOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lesson_id: uuid.UUID
    state: Literal["done", "partial", "none"]


class LeaderboardRowOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int
    participant_id: uuid.UUID
    display_name: str
    overall_progress: float = Field(ge=0, le=100)
    lesson_statuses: list[LessonStatusIconOut]
    medal: Literal["gold", "silver", "bronze"] | None = None


class ScatterPointOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    participant_id: uuid.UUID
    display_name: str
    x: float
    y: float
    rank: int


class LeaderboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scatter_meta: dict
    table: list[LeaderboardRowOut]
    scatter: list[ScatterPointOut]


class DialogMessageReadOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime


class DialogMessageListPageOut(CursorPageMixin):
    items: list[DialogMessageReadOut]


class ParticipantDialogBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(..., min_length=1)

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: object) -> str:
        if not isinstance(value, str):
            msg = "content must be a string"
            raise TypeError(msg)
        stripped = value.strip()
        if not stripped:
            msg = "content must be non-empty after trim"
            raise ValueError(msg)
        return stripped


class DataQueryRequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(..., min_length=1, max_length=2000)

    @field_validator("question", mode="before")
    @classmethod
    def strip_question(cls, value: object) -> str:
        if not isinstance(value, str):
            msg = "question must be a string"
            raise TypeError(msg)
        stripped = value.strip()
        if not stripped:
            msg = "question must be non-empty after trim"
            raise ValueError(msg)
        return stripped


class DataQueryResponseOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str
    params: dict[str, Any]
    result: list[dict[str, Any]]
    explanation: str
    correlation_id: uuid.UUID
