from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from core.db import Base
from enums.provider import ProviderType, PowerUnit


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True, default=uuid4)
    installation_id = Column(
        Integer,
        ForeignKey("installations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False)
    provider_type = Column(Enum(ProviderType), nullable=False)
    vendor = Column(String, nullable=False)
    model = Column(String, nullable=True)
    unit = Column(Enum(PowerUnit), nullable=False)
    login = Column(String, nullable=True)
    password = Column(String, nullable=True)
    last_value = Column(Numeric(12, 4), nullable=True)
    last_measurement_at = Column(DateTime(timezone=True), nullable=True)
    polling_interval_sec = Column(Integer, nullable=False)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    installation = relationship("Installation", back_populates="providers")

    def __repr__(self) -> str:
        return (
            f"<Provider id={self.id} "
            f"type={self.provider_type} "
            f"vendor={self.vendor} "
            f"unit={self.unit}>"
        )
