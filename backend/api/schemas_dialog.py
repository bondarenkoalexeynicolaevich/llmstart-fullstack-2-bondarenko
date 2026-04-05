"""Pydantic-схемы для POST /v1/dialog-messages (OpenAPI v1)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DialogMessageCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    flow_id: uuid.UUID
    telegram_user_id: int = Field(..., ge=1, le=2**63 - 1)
    content: str = Field(..., min_length=1)

    @field_validator("content", mode="before")
    @classmethod
    def strip_nonempty(cls, value: object) -> str:
        if not isinstance(value, str):
            msg = "content must be a string"
            raise TypeError(msg)
        stripped = value.strip()
        if not stripped:
            msg = "content must be non-empty after trim"
            raise ValueError(msg)
        return stripped


class DialogMessageCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply_text: str
    user_message_id: uuid.UUID
    assistant_message_id: uuid.UUID
