"""users.telegram_username partial unique lower case.

Teacher демо (@Bondarenko_Alexey_Nikolaevich, telegram_id=459032551): `data/progress-import.v1.json` + финальный UPDATE в `scripts/seed_data.py`.

Revision ID: 005_telegram_username
Revises: 004_knowledge_progress
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005_telegram_username"
down_revision: Union[str, None] = "004_knowledge_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("telegram_username", sa.String(length=255), nullable=True),
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_users_telegram_username_lower "
            "ON users (LOWER(telegram_username)) "
            "WHERE telegram_username IS NOT NULL",
        ),
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS uq_users_telegram_username_lower"))
    op.drop_column("users", "telegram_username")
