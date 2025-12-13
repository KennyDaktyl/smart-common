from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from smart_common.core.db import Base


class Installation(Base):
    __tablename__ = "installations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    station_code: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    station_addr: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="installations")
    providers = relationship("Provider", back_populates="installation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Installation(name={self.name}, station_code={self.station_code}, user_id={self.user_id})>"
