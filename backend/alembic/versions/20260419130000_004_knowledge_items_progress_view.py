"""knowledge_items (embedding float8[]), participant_assignment_progress view.

Revision ID: 004_knowledge_progress
Revises: 003_modules_lessons
Create Date: 2026-04-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_knowledge_progress"
down_revision: Union[str, None] = "003_modules_lessons"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Портативно без расширения pgvector: массив float8. При внедрении similarity search
    # можно отдельной миграцией перейти на тип vector + IVFFlat (см. docs/data-model.md).
    op.create_table(
        "knowledge_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.ARRAY(sa.Float(precision=53)), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["flow_id"], ["flows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_items_flow_id", "knowledge_items", ["flow_id"])

    op.execute(
        sa.text(
            """
            CREATE VIEW participant_assignment_progress AS
            SELECT
              p.id AS participant_id,
              p.flow_id,
              m.id AS module_id,
              m."order" AS module_order,
              l.id AS lesson_id,
              l."order" AS lesson_order,
              a.id AS assignment_id,
              s.status,
              s.submitted_at
            FROM participants p
            JOIN modules m ON m.flow_id = p.flow_id
            JOIN lessons l ON l.module_id = m.id
            JOIN assignments a ON a.lesson_id = l.id
            LEFT JOIN submissions s ON s.assignment_id = a.id AND s.participant_id = p.id
            """,
        ),
    )


def downgrade() -> None:
    op.execute(sa.text("DROP VIEW IF EXISTS participant_assignment_progress"))
    op.drop_index("ix_knowledge_items_flow_id", table_name="knowledge_items")
    op.drop_table("knowledge_items")
