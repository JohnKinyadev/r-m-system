"""add worker_permissions table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "worker_permissions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("module", sa.String(50), nullable=False),
        sa.UniqueConstraint("user_id", "module", name="uq_worker_module"),
    )


def downgrade() -> None:
    op.drop_table("worker_permissions")
