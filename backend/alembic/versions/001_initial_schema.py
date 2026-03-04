"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # block_status enum
    block_status = postgresql.ENUM(
        "planned", "in_progress", "done", "missed",
        name="block_status", create_type=True
    )
    block_status.create(op.get_bind())

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("color_hex", sa.String(7), nullable=False, server_default="#6366f1"),
        sa.Column("priority_weight", sa.SmallInteger, nullable=False, server_default="1"),
        sa.Column("weekly_target_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("daily_cap_minutes", sa.Integer, nullable=True),
        sa.Column("is_deep_work", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("priority_weight BETWEEN 1 AND 10", name="chk_priority_weight"),
    )
    op.create_index("ix_categories_priority_weight", "categories", ["priority_weight"], postgresql_ops={"priority_weight": "DESC"})

    op.create_table(
        "time_blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.Column("planned_duration", sa.Integer, nullable=False),
        sa.Column("status", sa.Enum("planned", "in_progress", "done", "missed", name="block_status"), nullable=False, server_default="planned"),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("end_time > start_time", name="chk_end_after_start"),
        sa.CheckConstraint("planned_duration > 0", name="chk_positive_duration"),
    )
    op.create_index("ix_time_blocks_date", "time_blocks", ["date"])
    op.create_index("ix_time_blocks_category_date", "time_blocks", ["category_id", "date"])
    op.create_index("ix_time_blocks_status", "time_blocks", ["status"],
                    postgresql_where=sa.text("status != 'done'"))

    op.create_table(
        "time_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("time_block_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_duration", sa.Integer, nullable=True),
        sa.Column("interruptions", sa.SmallInteger, nullable=False, server_default="0"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["time_block_id"], ["time_blocks.id"], ondelete="CASCADE"),
        sa.CheckConstraint("actual_duration IS NULL OR actual_duration >= 0", name="chk_non_negative_duration"),
    )
    op.create_index("ix_time_logs_actual_start", "time_logs", ["actual_start"])
    op.create_index("ix_time_logs_active", "time_logs", ["time_block_id"],
                    unique=True, postgresql_where=sa.text("actual_end IS NULL"))

    op.create_table(
        "daily_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("date", sa.Date, nullable=False, unique=True),
        sa.Column("energy_rating", sa.SmallInteger, nullable=False),
        sa.Column("sleep_hours", sa.Numeric(3, 1), nullable=False),
        sa.Column("gym_done", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("energy_rating BETWEEN 1 AND 5", name="chk_energy_rating"),
        sa.CheckConstraint("sleep_hours BETWEEN 0 AND 24", name="chk_sleep_hours"),
    )
    op.create_index("ix_daily_reviews_date", "daily_reviews", ["date"])


def downgrade() -> None:
    op.drop_table("daily_reviews")
    op.drop_table("time_logs")
    op.drop_table("time_blocks")
    op.drop_table("categories")
    op.execute("DROP TYPE IF EXISTS block_status")
