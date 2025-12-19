from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import ConfigDict, Field

from smart_common.enums.unit import PowerUnit
from smart_common.providers.enums import ProviderKind, ProviderType, ProviderVendor
from smart_common.schemas.base import APIModel, ORMModel


class ProviderCreateRequest(APIModel):
    name: str = Field(..., description="Friendly provider name")

    provider_type: ProviderType = Field(
        ...,
        description="Source category of the provider",
    )

    kind: ProviderKind = Field(
        ...,
        description="Domain of measurements supplied by the provider",
    )

    vendor: Optional[ProviderVendor] = Field(
        None,
        description="Vendor identifier",
    )

    unit: Optional[PowerUnit] = Field(
        None,
        description="Measurement unit",
    )

    value_min: float = Field(
        ...,
        description="Physical minimum value",
        example=0.0,
    )

    value_max: float = Field(
        ...,
        description="Physical maximum value",
        example=20.0,
    )

    enabled: bool = Field(
        True,
        description="Whether provider is enabled",
    )

    config: Dict[str, Any] = Field(
        ...,
        description="Vendor-specific provider configuration",
    )


class ProviderUpdateRequest(APIModel):
    name: Optional[str] = None
    vendor: Optional[ProviderVendor] = None
    unit: Optional[PowerUnit] = None

    value_min: Optional[float] = None
    value_max: Optional[float] = None

    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class ProviderResponse(ORMModel):
    id: int
    uuid: UUID
    microcontroller_id: int

    name: str
    provider_type: ProviderType
    kind: ProviderKind
    vendor: Optional[ProviderVendor]
    unit: Optional[PowerUnit]

    value_min: Optional[float]
    value_max: Optional[float]

    last_value: Optional[float]
    last_measurement_at: Optional[datetime]

    enabled: bool
    config: Dict[str, Any]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class ProviderStatusRequest(APIModel):
    enabled: bool
