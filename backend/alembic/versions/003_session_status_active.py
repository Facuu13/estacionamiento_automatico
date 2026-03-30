"""add active to session_status enum

Revision ID: 003_session_status_active
Revises: 002_device_commands
Create Date: 2026-03-30

"""

from typing import Sequence, Union

from alembic import op

revision: str = "003_session_status_active"
down_revision: Union[str, None] = "002_device_commands"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE session_status ADD VALUE IF NOT EXISTS 'active'")


def downgrade() -> None:
    pass
