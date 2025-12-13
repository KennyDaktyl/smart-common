from __future__ import annotations

from uuid import UUID as UUIDType, uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smart_common.core.db import Base


class Raspberry(Base):
    __tablename__ = "raspberries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[UUIDType] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid4, index=True)
    secret_key: Mapped[str] = mapped_column(String, nullable=False)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    software_version: Mapped[str | None] = mapped_column(String, nullable=True)

    max_devices: Mapped[int] = mapped_column(Integer, default=1)

    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    provider_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("providers.id", ondelete="SET NULL"), nullable=True, index=True)

    user = relationship("User", back_populates="raspberries")
    provider = relationship("Provider", back_populates="raspberries")

    devices = relationship("Device", back_populates="raspberry", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        provider_part = f" provider_id={self.provider_id}" if self.provider_id else ""
        return f"<Raspberry id={self.id} name={self.name} uuid={self.uuid}{provider_part}>"
