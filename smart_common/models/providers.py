from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID as UUIDType, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, Numeric, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smart_common.core.db import Base
from smart_common.enums.provider import (
    ProviderType,
    PowerUnit,
    ProviderKind,
    ProviderVendor,
)


class Provider(Base):
    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True, default=uuid4
    )
    installation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("installations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, name="provider_type_enum"), nullable=False
    )
    kind: Mapped[ProviderKind] = mapped_column(
        Enum(ProviderKind, name="provider_kind_enum"), nullable=False
    )
    vendor: Mapped[ProviderVendor | None] = mapped_column(Enum(ProviderVendor), nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    unit: Mapped[PowerUnit] = mapped_column(Enum(PowerUnit, name="power_unit_enum"), nullable=False)
    min_value: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    max_value: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    last_value: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    last_measurement_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    polling_interval_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    installation = relationship("Installation", back_populates="providers")
    raspberries = relationship(
        "Raspberry", back_populates="provider", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Provider id={self.id} "
            f"kind={self.kind} "
            f"type={self.provider_type} "
            f"vendor={self.vendor} "
            f"unit={self.unit}>"
        )
