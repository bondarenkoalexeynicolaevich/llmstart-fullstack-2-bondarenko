"""Pydantic-схемы для POST /v1/submissions (OpenAPI v1)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    flow_id: uuid.UUID
    telegram_user_id: int = Field(..., ge=1, le=2**63 - 1)
    assignment_id: uuid.UUID
    comment: str | None = None


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    assignment_id: uuid.UUID
    participant_id: uuid.UUID
    status: str
    submitted_at: datetime
    comment: str | None = None
