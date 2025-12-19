"""auto migration 2025-12-19T10:53:30.595067+00:00

Revision ID: a71eb11e5acb
Revises: ff7d4a413a4a
Create Date: 2025-12-19 11:53:30.831561
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a71eb11e5acb"
down_revision: Union[str, Sequence[str], None] = "ff7d4a413a4a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --------------------------------------------------
    # DEVICE EVENTS – comments only (SAFE)
    # --------------------------------------------------
    op.alter_column(
        "device_events",
        "device_state",
        existing_type=sa.VARCHAR(),
        comment="Logical state (e.g., ON/OFF)",
        existing_comment="Stan logiczny (np. ON/OFF)",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "pin_state",
        existing_type=sa.BOOLEAN(),
        comment="Physical GPIO/relay state",
        existing_comment="Fizyczny stan GPIO / przekaźnika",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "measured_value",
        existing_type=sa.NUMERIC(precision=12, scale=4),
        comment="Value reported by the provider (e.g., power, temperature)",
        existing_comment="Wartość z providera (np. moc, temp)",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "measured_unit",
        existing_type=sa.VARCHAR(length=16),
        comment="Measurement unit (W, kW, C, %)",
        existing_comment="Jednostka (W, kW, C, %)",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "trigger_reason",
        existing_type=sa.VARCHAR(),
        comment="Reason why the event occurred",
        existing_comment="Dlaczego zdarzenie wystąpiło",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "source",
        existing_type=sa.VARCHAR(),
        comment="Source identifier (controller / agent / api)",
        existing_comment="controller / agent / api",
        existing_nullable=True,
    )

    # --------------------------------------------------
    # INSTALLATIONS – SAFE TIMESTAMPS
    # --------------------------------------------------

    # is_active – OK (server_default)
    op.add_column(
        "installations",
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
    )

    # created_at – OK (server_default)
    op.add_column(
        "installations",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # updated_at – 3-STEP SAFE MIGRATION
    op.add_column(
        "installations",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,  # STEP 1
        ),
    )

    # STEP 2 – backfill existing rows
    op.execute(sa.text("UPDATE installations SET updated_at = NOW() WHERE updated_at IS NULL"))

    # STEP 3 – enforce NOT NULL
    op.alter_column(
        "installations",
        "updated_at",
        nullable=False,
    )

    # --------------------------------------------------
    # USER PROFILES
    # --------------------------------------------------
    op.alter_column(
        "user_profiles",
        "company_vat",
        existing_type=sa.VARCHAR(length=32),
        type_=sa.String(length=64),
        existing_nullable=True,
    )
    op.alter_column(
        "user_profiles",
        "company_address",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.String(length=512),
        existing_nullable=True,
    )
    op.alter_column(
        "user_profiles",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )

    op.drop_column("user_profiles", "phone")
    op.drop_column("user_profiles", "tax_id")


def downgrade() -> None:
    # --------------------------------------------------
    # USER PROFILES
    # --------------------------------------------------
    op.add_column(
        "user_profiles",
        sa.Column("tax_id", sa.VARCHAR(length=32), nullable=True),
    )
    op.add_column(
        "user_profiles",
        sa.Column("phone", sa.VARCHAR(length=32), nullable=True),
    )
    op.alter_column(
        "user_profiles",
        "created_at",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "user_profiles",
        "company_address",
        existing_type=sa.String(length=512),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "user_profiles",
        "company_vat",
        existing_type=sa.String(length=64),
        type_=sa.VARCHAR(length=32),
        existing_nullable=True,
    )

    # --------------------------------------------------
    # INSTALLATIONS
    # --------------------------------------------------
    op.drop_column("installations", "updated_at")
    op.drop_column("installations", "created_at")
    op.drop_column("installations", "is_active")

    # --------------------------------------------------
    # DEVICE EVENTS – comments revert
    # --------------------------------------------------
    op.alter_column(
        "device_events",
        "source",
        existing_type=sa.VARCHAR(),
        comment="controller / agent / api",
        existing_comment="Source identifier (controller / agent / api)",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "trigger_reason",
        existing_type=sa.VARCHAR(),
        comment="Dlaczego zdarzenie wystąpiło",
        existing_comment="Reason why the event occurred",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "measured_unit",
        existing_type=sa.VARCHAR(length=16),
        comment="Jednostka (W, kW, C, %)",
        existing_comment="Measurement unit (W, kW, C, %)",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "measured_value",
        existing_type=sa.NUMERIC(precision=12, scale=4),
        comment="Wartość z providera (np. moc, temp)",
        existing_comment="Value reported by the provider (e.g., power, temperature)",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "pin_state",
        existing_type=sa.BOOLEAN(),
        comment="Fizyczny stan GPIO / przekaźnika",
        existing_comment="Physical GPIO/relay state",
        existing_nullable=True,
    )
    op.alter_column(
        "device_events",
        "device_state",
        existing_type=sa.VARCHAR(),
        comment="Stan logiczny (np. ON/OFF)",
        existing_comment="Logical state (e.g., ON/OFF)",
        existing_nullable=True,
    )
