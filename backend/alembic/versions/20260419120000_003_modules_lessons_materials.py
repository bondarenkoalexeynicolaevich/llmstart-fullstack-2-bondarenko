"""modules, lessons, materials; assignments.lesson_id; users email + partial unique.

Revision ID: 003_modules_lessons
Revises: 002_dialog_submissions
Create Date: 2026-04-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_modules_lessons"
down_revision: Union[str, None] = "002_dialog_submissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

material_type = postgresql.ENUM(
    "link",
    "file",
    "text",
    name="material_type",
    create_type=True,
)


def upgrade() -> None:
    op.create_table(
        "modules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("flow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["flow_id"], ["flows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("flow_id", "order", name="uq_modules_flow_order"),
    )
    op.create_index("ix_modules_flow_id", "modules", ["flow_id"])

    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module_id", "order", name="uq_lessons_module_order"),
    )
    op.create_index("ix_lessons_module_id", "lessons", ["module_id"])

    op.create_table(
        "materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("type", material_type, nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(type::text = 'text' AND content IS NOT NULL) OR "
            "(type::text IN ('link', 'file') AND url IS NOT NULL)",
            name="ck_materials_type_payload",
        ),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_materials_lesson_id", "materials", ["lesson_id"])

    op.execute(sa.text("DELETE FROM submissions"))
    op.execute(sa.text("DELETE FROM assignments"))

    op.drop_constraint("assignments_flow_id_fkey", "assignments", type_="foreignkey")
    op.drop_column("assignments", "flow_id")

    op.add_column(
        "assignments",
        sa.Column("lesson_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "assignments_lesson_id_fkey",
        "assignments",
        "lessons",
        ["lesson_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_assignments_lesson_id", "assignments", ["lesson_id"])

    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=512),
        nullable=True,
    )
    op.execute(sa.text("UPDATE users SET email = NULL WHERE email = ''"))

    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_users_telegram_id_not_null ON users (telegram_id) "
            "WHERE telegram_id IS NOT NULL",
        ),
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX uq_users_email_lower_not_null ON users (LOWER(email)) "
            "WHERE email IS NOT NULL",
        ),
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS uq_users_email_lower_not_null"))
    op.execute(sa.text("DROP INDEX IF EXISTS uq_users_telegram_id_not_null"))

    op.execute(sa.text("UPDATE users SET email = '' WHERE email IS NULL"))
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=512),
        nullable=False,
    )

    op.execute(sa.text("DELETE FROM submissions"))
    op.execute(sa.text("DELETE FROM assignments"))

    op.drop_index("ix_assignments_lesson_id", table_name="assignments")
    op.drop_constraint("assignments_lesson_id_fkey", "assignments", type_="foreignkey")
    op.drop_column("assignments", "lesson_id")

    op.add_column(
        "assignments",
        sa.Column("flow_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.create_foreign_key(
        "assignments_flow_id_fkey",
        "assignments",
        "flows",
        ["flow_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_index("ix_materials_lesson_id", table_name="materials")
    op.drop_table("materials")
    op.execute(sa.text("DROP TYPE IF EXISTS material_type"))

    op.drop_index("ix_lessons_module_id", table_name="lessons")
    op.drop_table("lessons")

    op.drop_index("ix_modules_flow_id", table_name="modules")
    op.drop_table("modules")
