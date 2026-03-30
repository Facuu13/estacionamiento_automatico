"""device_commands for ESP32 gate pulse

Revision ID: 002_device_commands
Revises: 001_initial
Create Date: 2026-03-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_device_commands"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_commands",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("nonce", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.BigInteger(), nullable=False),
        sa.Column("pulse_seconds", sa.Integer(), nullable=False),
        sa.Column("signature_hex", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_device_commands_device_id"), "device_commands", ["device_id"], unique=False)
    op.create_index(op.f("ix_device_commands_nonce"), "device_commands", ["nonce"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_device_commands_nonce"), table_name="device_commands")
    op.drop_index(op.f("ix_device_commands_device_id"), table_name="device_commands")
    op.drop_table("device_commands")
