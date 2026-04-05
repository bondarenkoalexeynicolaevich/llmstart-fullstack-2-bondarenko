"""Сообщение диалога участника с ассистентом."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.enums import DialogMessageRole

if TYPE_CHECKING:
    from backend.models.participant import Participant


class DialogMessage(Base):
    __tablename__ = "dialog_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[DialogMessageRole] = mapped_column(
        SAEnum(DialogMessageRole, name="dialog_message_role", native_enum=True),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    participant: Mapped[Participant] = relationship(
        "Participant", back_populates="dialog_messages"
    )
