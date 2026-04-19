"""Модель Flow."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.knowledge_item import KnowledgeItem
    from backend.models.module import Module
    from backend.models.participant import Participant


class Flow(Base):
    __tablename__ = "flows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    started_at: Mapped[date] = mapped_column(Date(), nullable=False)
    finished_at: Mapped[date | None] = mapped_column(Date(), nullable=True)

    participants: Mapped[list[Participant]] = relationship(
        "Participant", back_populates="flow"
    )
    modules: Mapped[list[Module]] = relationship(
        "Module",
        back_populates="flow",
        order_by="Module.order",
    )
    knowledge_items: Mapped[list[KnowledgeItem]] = relationship(
        "KnowledgeItem",
        back_populates="flow",
    )
