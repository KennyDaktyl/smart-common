"""auto migration 2025-12-13T10:24:36+00:00

Revision ID: 5cb3f720cb5e
Revises: 
Create Date: 2025-12-13 11:24:36.632203
"""
from alembic import op
import sqlalchemy as sa

to_timestamp = sa.func.now()

# revision identifiers, used by Alembic.
revision = '5cb3f720cb5e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    userrole = sa.Enum("admin", "client", "client_pro", "demo", name="userrole")
    providertype = sa.Enum("api", "sensor", "virtual", name="providertype")
    powerunit = sa.Enum("W", "kW", "lux", "C", "%", name="powerunit")
    devicemode = sa.Enum("MANUAL", "AUTO", "SCHEDULE", name="devicemode")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=to_timestamp, nullable=False),
        sa.Column("role", userrole, nullable=False, server_default="client"),
    )

    op.create_table(
        "installations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("station_code", sa.String(length=255), nullable=False, unique=True),
        sa.Column("station_addr", sa.String(length=255), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )

    op.create_index("ix_installations_id", "installations", ["id"], unique=False)

    op.create_table(
        "raspberries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("secret_key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("software_version", sa.String(), nullable=True),
        sa.Column("max_devices", sa.Integer(), server_default="1", nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    op.create_index("ix_raspberries_uuid", "raspberries", ["uuid"], unique=False)

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("uuid", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raspberry_id", sa.Integer(), sa.ForeignKey("raspberries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_number", sa.Integer(), nullable=False),
        sa.Column("rated_power_kw", sa.Numeric(), nullable=True),
        sa.Column("mode", devicemode, nullable=False, server_default="MANUAL"),
        sa.Column("threshold_kw", sa.Numeric(), nullable=True),
        sa.Column("hysteresis_w", sa.Numeric(), nullable=False, server_default="100"),
        sa.Column("schedule", sa.JSON(), nullable=True),
        sa.Column("last_update", sa.DateTime(timezone=True), server_default=to_timestamp, nullable=False),
        sa.Column("manual_state", sa.Boolean(), nullable=True),
    )

    op.create_index("ix_devices_uuid", "devices", ["uuid"], unique=False)

    op.create_table(
        "providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("uuid", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column(
            "installation_id",
            sa.Integer(),
            sa.ForeignKey("installations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("provider_type", providertype, nullable=False),
        sa.Column("vendor", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("unit", powerunit, nullable=False),
        sa.Column("last_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("last_measurement_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("polling_interval_sec", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("login", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=to_timestamp, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=to_timestamp, nullable=False),
    )

    op.create_index("ix_providers_installation_id", "providers", ["installation_id"], unique=False)
    op.create_index("ix_providers_uuid", "providers", ["uuid"], unique=False)

    op.create_table(
        "device_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_name", sa.String(), nullable=False, server_default="DEVICE_STATE"),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("pin_state", sa.Boolean(), nullable=False),
        sa.Column("trigger_reason", sa.String(), nullable=True),
        sa.Column("power_kw", sa.Numeric(10, 2), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=to_timestamp, nullable=False),
    )

    op.create_table(
        "device_schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("day_of_week", sa.String(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("mode", devicemode, nullable=False, server_default="AUTO"),
        sa.Column("threshold_kw", sa.Numeric(10, 3), nullable=True),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )

    op.create_table(
        "provider_power_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_id", sa.Integer(), sa.ForeignKey("providers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("current_power", sa.Numeric(10, 2), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=to_timestamp, nullable=False),
    )

    op.create_index("ix_provider_power_records_id", "provider_power_records", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_provider_power_records_id", table_name="provider_power_records")
    op.drop_table("provider_power_records")
    op.drop_table("device_schedules")
    op.drop_table("device_events")
    op.drop_index("ix_providers_uuid", table_name="providers")
    op.drop_index("ix_providers_installation_id", table_name="providers")
    op.drop_table("providers")
    op.drop_index("ix_devices_uuid", table_name="devices")
    op.drop_table("devices")
    op.drop_index("ix_raspberries_uuid", table_name="raspberries")
    op.drop_table("raspberries")
    op.drop_index("ix_installations_id", table_name="installations")
    op.drop_table("installations")
    op.drop_table("users")

    devicemode = sa.Enum("MANUAL", "AUTO", "SCHEDULE", name="devicemode")
    devicemode.drop(op.get_bind(), checkfirst=True)

    powerunit = sa.Enum("W", "kW", "lux", "C", "%", name="powerunit")
    powerunit.drop(op.get_bind(), checkfirst=True)

    providertype = sa.Enum("api", "sensor", "virtual", name="providertype")
    providertype.drop(op.get_bind(), checkfirst=True)

    userrole = sa.Enum("admin", "client", "client_pro", "demo", name="userrole")
    userrole.drop(op.get_bind(), checkfirst=True)
