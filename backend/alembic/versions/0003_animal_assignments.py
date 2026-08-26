"""add animal_assignments table

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-03
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "animal_assignments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("animal_id", sa.Integer, sa.ForeignKey("animals.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("worker_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("animal_id", "worker_id", name="uq_animal_worker"),
    )


def downgrade() -> None:
    op.drop_table("animal_assignments")
