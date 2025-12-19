from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID as UUIDType
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smart_common.core.db import Base
from smart_common.providers.enums import ProviderKind, ProviderType, ProviderVendor
from smart_common.enums.unit import PowerUnit


class Provider(Base):
    __tablename__ = "providers"

    # ---------- identity ----------
    id: Mapped[int] = mapped_column(primary_key=True)

    uuid: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
        index=True,
    )

    microcontroller_id: Mapped[int] = mapped_column(
        ForeignKey("microcontrollers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    # ---------- classification ----------
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, name="provider_type_enum"),
        nullable=False,
    )

    kind: Mapped[ProviderKind] = mapped_column(
        Enum(ProviderKind, name="provider_kind_enum"),
        nullable=False,
    )

    vendor: Mapped[ProviderVendor | None] = mapped_column(
        Enum(ProviderVendor, name="provider_vendor_enum"),
        nullable=True,
    )

    unit: Mapped[PowerUnit | None] = mapped_column(
        Enum(PowerUnit, name="power_unit_enum"),
        nullable=True,
    )

    # ---------- physical range (NOT scheduler rules) ----------
    value_min: Mapped[float | None] = mapped_column(Numeric(12, 4))
    value_max: Mapped[float | None] = mapped_column(Numeric(12, 4))

    # ---------- runtime state ----------
    last_value: Mapped[float | None] = mapped_column(Numeric(12, 4))
    last_measurement_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    # ---------- lifecycle ----------
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # ---------- vendor-specific config ----------
    config: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    microcontroller = relationship(
        "Microcontroller",
        back_populates="providers",
    )
