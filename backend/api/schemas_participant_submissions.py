"""Схемы списка сдач участника."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ParticipantSubmissionRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    assignment_id: uuid.UUID
    status: str
    submitted_at: datetime
    comment: str | None = None
