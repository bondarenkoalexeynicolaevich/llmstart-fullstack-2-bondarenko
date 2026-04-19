"""Перечисления домена (согласованы с docs/data-model.md)."""

from __future__ import annotations

import enum


class MemberRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"


class DialogMessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class SubmissionStatus(str, enum.Enum):
    submitted = "submitted"
    reviewed = "reviewed"
    approved = "approved"


class MaterialType(str, enum.Enum):
    link = "link"
    file = "file"
    text = "text"
