"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-23
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── roles ────────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
    )

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── livestock_types ──────────────────────────────────────────────────────
    op.create_table(
        "livestock_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("breed", sa.String(100), nullable=True),
        sa.Column("gestation_period_days", sa.Integer(), nullable=True),
        sa.Column("average_lifespan_years", sa.Float(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── vaccine_schedules ────────────────────────────────────────────────────
    op.create_table(
        "vaccine_schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("livestock_type_id", sa.Integer(), sa.ForeignKey("livestock_types.id", ondelete="CASCADE"), nullable=False),
        sa.Column("vaccine_name", sa.String(150), nullable=False),
        sa.Column("first_dose_age_days", sa.Integer(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=True),
    )

    # ── animals ──────────────────────────────────────────────────────────────
    animal_status = sa.Enum("active", "sold", "deceased", name="animalstatus")
    animal_gender = sa.Enum("male", "female", name="animalgender")

    op.create_table(
        "animals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tag_number", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("livestock_type_id", sa.Integer(), sa.ForeignKey("livestock_types.id"), nullable=False),
        sa.Column("gender", animal_gender, nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("mother_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("father_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("status", animal_status, nullable=False, server_default="active"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_animals_tag_number", "animals", ["tag_number"], unique=True)

    # ── mating_events ────────────────────────────────────────────────────────
    op.create_table(
        "mating_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("female_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("male_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("mating_date", sa.Date(), nullable=False),
        sa.Column("expected_birth_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("logged_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── births ───────────────────────────────────────────────────────────────
    op.create_table(
        "births",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mating_event_id", sa.Integer(), sa.ForeignKey("mating_events.id"), nullable=True),
        sa.Column("animal_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("number_of_offspring", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("logged_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── health_logs ──────────────────────────────────────────────────────────
    health_log_type = sa.Enum(
        "observation", "vaccination", "treatment", "weight", "deworming",
        name="healthlogtype",
    )
    op.create_table(
        "health_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("animal_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("log_type", health_log_type, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("vaccine_name", sa.String(150), nullable=True),
        sa.Column("logged_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── feed_types ───────────────────────────────────────────────────────────
    op.create_table(
        "feed_types",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False, unique=True),
        sa.Column("unit", sa.String(50), nullable=False, server_default="kg"),
        sa.Column("current_stock", sa.Float(), nullable=False, server_default="0"),
        sa.Column("low_stock_threshold", sa.Float(), nullable=False, server_default="50"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── feed_logs ────────────────────────────────────────────────────────────
    op.create_table(
        "feed_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feed_type_id", sa.Integer(), sa.ForeignKey("feed_types.id"), nullable=False),
        sa.Column("total_quantity", sa.Float(), nullable=False),
        sa.Column("session_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("logged_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── feed_distributions ───────────────────────────────────────────────────
    op.create_table(
        "feed_distributions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feed_log_id", sa.Integer(), sa.ForeignKey("feed_logs.id"), nullable=False),
        sa.Column("animal_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
    )

    # ── feed_stock_arrivals ──────────────────────────────────────────────────
    op.create_table(
        "feed_stock_arrivals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("feed_type_id", sa.Integer(), sa.ForeignKey("feed_types.id"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(300), nullable=True),
        sa.Column("arrived_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("logged_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── notifications ────────────────────────────────────────────────────────
    notification_type = sa.Enum(
        "birth_alert", "vaccination_due", "feed_stock_low", "missed_feeding", "general",
        name="notificationtype",
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("related_animal_id", sa.Integer(), sa.ForeignKey("animals.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("feed_stock_arrivals")
    op.drop_table("feed_distributions")
    op.drop_table("feed_logs")
    op.drop_table("feed_types")
    op.drop_table("health_logs")
    op.drop_table("births")
    op.drop_table("mating_events")
    op.drop_table("animals")
    op.drop_table("vaccine_schedules")
    op.drop_table("livestock_types")
    op.drop_table("users")
    op.drop_table("roles")

    sa.Enum(name="notificationtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="healthlogtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="animalgender").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="animalstatus").drop(op.get_bind(), checkfirst=True)
