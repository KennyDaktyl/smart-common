from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from smart_common.core.db import Base


class DeviceEvent(Base):
    __tablename__ = "device_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"))

    event_name: Mapped[str] = mapped_column(String, default="DEVICE_STATE", nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    pin_state: Mapped[bool] = mapped_column(Boolean, nullable=False)
    trigger_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    power_kw: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return (
            f"<DeviceEvent(event_name={self.event_name}, device_id={self.device_id}, "
            f"state={self.state}, pin_state={self.pin_state}, timestamp={self.timestamp})>"
        )
