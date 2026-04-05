"""Модель Participant."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.enums import MemberRole

if TYPE_CHECKING:
    from backend.models.dialog_message import DialogMessage
    from backend.models.flow import Flow
    from backend.models.submission import Submission
    from backend.models.user import User


class Participant(Base):
    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint("user_id", "flow_id", name="uq_participants_user_flow"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    flow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("flows.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MemberRole] = mapped_column(
        SAEnum(MemberRole, name="member_role", native_enum=True),
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="participants")
    flow: Mapped[Flow] = relationship("Flow", back_populates="participants")
    dialog_messages: Mapped[list[DialogMessage]] = relationship(
        "DialogMessage", back_populates="participant"
    )
    submissions: Mapped[list[Submission]] = relationship(
        "Submission", back_populates="participant"
    )
