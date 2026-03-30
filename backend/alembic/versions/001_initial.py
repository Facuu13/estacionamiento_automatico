"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-03-30

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    session_status = sa.Enum(
        "pending_payment",
        "paid",
        "exited",
        name="session_status",
        create_constraint=True,
    )
    payment_status = sa.Enum(
        "pending",
        "approved",
        "rejected",
        "refunded",
        name="payment_status",
        create_constraint=True,
    )

    op.create_table(
        "parking_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("license_plate", sa.String(length=32), nullable=False),
        sa.Column("gate_code", sa.String(length=64), nullable=False),
        sa.Column("status", session_status, nullable=False),
        sa.Column("exit_token", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exited_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parking_sessions_exit_token"), "parking_sessions", ["exit_token"], unique=True)
    op.create_index(op.f("ix_parking_sessions_license_plate"), "parking_sessions", ["license_plate"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("mp_preference_id", sa.String(length=64), nullable=True),
        sa.Column("mp_init_point", sa.String(length=512), nullable=True),
        sa.Column("mp_payment_id", sa.String(length=64), nullable=True),
        sa.Column("status", payment_status, nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["parking_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_mp_payment_id"), "payments", ["mp_payment_id"], unique=False)
    op.create_index(op.f("ix_payments_mp_preference_id"), "payments", ["mp_preference_id"], unique=False)
    op.create_index(op.f("ix_payments_session_id"), "payments", ["session_id"], unique=False)

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=256), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("payload_summary", sa.Text(), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_events_idempotency_key"), "webhook_events", ["idempotency_key"], unique=True)

    op.create_table(
        "devices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("firmware_version", sa.String(length=32), nullable=True),
        sa.Column("last_rssi", sa.Integer(), nullable=True),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_devices_device_id"), "devices", ["device_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_devices_device_id"), table_name="devices")
    op.drop_table("devices")
    op.drop_index(op.f("ix_webhook_events_idempotency_key"), table_name="webhook_events")
    op.drop_table("webhook_events")
    op.drop_index(op.f("ix_payments_session_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_mp_preference_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_mp_payment_id"), table_name="payments")
    op.drop_table("payments")
    op.drop_index(op.f("ix_parking_sessions_license_plate"), table_name="parking_sessions")
    op.drop_index(op.f("ix_parking_sessions_exit_token"), table_name="parking_sessions")
    op.drop_table("parking_sessions")
    op.execute(sa.text("DROP TYPE IF EXISTS payment_status CASCADE"))
    op.execute(sa.text("DROP TYPE IF EXISTS session_status CASCADE"))
