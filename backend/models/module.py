"""Модель Module (модуль внутри потока)."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.flow import Flow
    from backend.models.lesson import Lesson


class Module(Base):
    __tablename__ = "modules"
    __table_args__ = (
        UniqueConstraint("flow_id", "order", name="uq_modules_flow_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    flow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flows.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    order: Mapped[int] = mapped_column(Integer(), nullable=False)

    flow: Mapped[Flow] = relationship("Flow", back_populates="modules")
    lessons: Mapped[list[Lesson]] = relationship(
        "Lesson",
        back_populates="module",
        order_by="Lesson.order",
    )
