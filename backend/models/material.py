"""Модель Material (материал занятия)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.enums import MaterialType

if TYPE_CHECKING:
    from backend.models.lesson import Lesson


class Material(Base):
    __tablename__ = "materials"
    __table_args__ = (
        CheckConstraint(
            "(type = 'text' AND content IS NOT NULL) OR "
            "(type IN ('link', 'file') AND url IS NOT NULL)",
            name="ck_materials_type_payload",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[MaterialType] = mapped_column(
        SAEnum(MaterialType, name="material_type", native_enum=True),
        nullable=False,
    )
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    content: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lesson: Mapped[Lesson] = relationship("Lesson", back_populates="materials")
