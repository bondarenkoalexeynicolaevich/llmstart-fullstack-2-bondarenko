"""ORM-модели; импорт для регистрации metadata и Alembic."""

from backend.models.assignment import Assignment
from backend.models.base import Base
from backend.models.dialog_message import DialogMessage
from backend.models.enums import DialogMessageRole, MemberRole, SubmissionStatus
from backend.models.flow import Flow
from backend.models.participant import Participant
from backend.models.submission import Submission
from backend.models.user import User

__all__ = [
    "Assignment",
    "Base",
    "DialogMessage",
    "DialogMessageRole",
    "Flow",
    "MemberRole",
    "Participant",
    "Submission",
    "SubmissionStatus",
    "User",
]
