"""Схемы read API: модули и занятия."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LessonRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    title: str
    order: int = Field(..., ge=0)
    scheduled_at: datetime | None = None


class ModuleRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    title: str
    order: int = Field(..., ge=0)
    lessons: list[LessonRead]
