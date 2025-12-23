from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import ConfigDict, Field

from smart_common.enums.microcontroller import MicrocontrollerType
from smart_common.enums.sensor import SensorType
from smart_common.schemas.base import APIModel, ORMModel
from smart_common.schemas.device_schema import DeviceResponse
from smart_common.schemas.provider_schema import ProviderResponse
from smart_common.schemas.pagination_schema import PaginationQuery


class MicrocontrollerCreateRequest(APIModel):
    name: str = Field(
        ..., description="Display name for the microcontroller", example="Gateway Alpha"
    )
    description: Optional[str] = Field(
        None,
        description="Additional notes or location details",
        example="Installed on rooftop, north side",
    )
    software_version: Optional[str] = Field(
        None,
        description="Firmware version running on the controller",
        example="1.4.2",
    )
    type: MicrocontrollerType = Field(
        MicrocontrollerType.RASPBERRY_PI_ZERO,
        description="Hardware type of the microcontroller",
        example=MicrocontrollerType.RASPBERRY_PI_ZERO.value,
    )
    max_devices: int = Field(
        4,
        gt=0,
        description="Maximum number of devices that can be attached",
        example=4,
    )
    assigned_sensors: List[str] = Field(
        default_factory=list,
        description="Physical sensors wired to this microcontroller (sensor code strings)",
        example=[SensorType.DHT22.value, SensorType.BH1750.value],
    )


class MicrocontrollerUpdateRequest(APIModel):
    name: Optional[str] = Field(None, description="Updated display name")
    description: Optional[str] = Field(None, description="Updated location notes")
    software_version: Optional[str] = Field(None, description="Firmware version")
    max_devices: Optional[int] = Field(
        None, gt=0, description="Updated device capacity"
    )
    enabled: Optional[bool] = Field(None, description="Toggle controller availability")


class MicrocontrollerStatusRequest(APIModel):
    enabled: bool = Field(
        ...,
        description="True to allow communication, false to pause the controller",
        example=True,
    )


class MicrocontrollerPowerProviderRequest(APIModel):
    provider_uuid: Optional[UUID] = Field(
        None,
        description="Selected API power provider UUID (null detaches the provider)",
    )


class MicrocontrollerAttachProviderRequest(APIModel):
    provider_id: Optional[UUID] = Field(
        None,
        description="Provider UUID to attach (null detaches and falls back to manual/scheduled)",
    )


class MicrocontrollerSensorsResponse(APIModel):
    assigned_sensors: List[str] = Field(
        default_factory=list,
        description="Physical sensors wired to this microcontroller",
        example=[SensorType.DHT22.value, SensorType.BH1750.value],
    )


class MicrocontrollerSensorsUpdateRequest(APIModel):
    assigned_sensors: List[str] = Field(
        ...,
        description="Replace assigned sensors for this microcontroller (empty list clears hardware assignments)",
        example=[SensorType.DHT22.value, SensorType.BME280.value],
    )


class MicrocontrollerResponse(ORMModel):
    id: int
    uuid: UUID
    user_id: int

    # ---- DEPRECATED (frontend backward compat) ----
    sensor_providers: Optional[List[ProviderResponse]] = Field(default=None)
    power_provider: Optional[ProviderResponse] = Field(default=None)

    # ---- CURRENT CONTRACT ----
    active_provider: Optional[ProviderResponse] = Field(
        None,
        description="Currently attached provider (API or sensor-derived)",
    )

    available_sensor_providers: List[ProviderResponse] = Field(
        default_factory=list,
        description="Providers derived from assigned physical sensors",
    )

    available_api_providers: List[ProviderResponse] = Field(
        default_factory=list,
        description="API providers available for this user",
    )

    devices: List[DeviceResponse] = Field(default_factory=list)

    # ---- META ----
    name: str
    description: Optional[str]
    software_version: Optional[str]
    type: MicrocontrollerType
    max_devices: int

    assigned_sensors: List[str] = Field(default_factory=list)

    enabled: bool
    created_at: datetime
    updated_at: datetime

    # ---- ADMIN ONLY ----
    user_email: Optional[str] = Field(
        None,
        description="Owner email (admin views only)",
    )

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class MicrocontrollerListQuery(PaginationQuery):
    """
    Query params for admin microcontroller list
    """

    admin_list: bool = Query(
        False,
        description="Admin only: list all microcontrollers in system",
        example=True,
    )

    user_id: Optional[int] = Query(
        None,
        description="Filter by owner user ID",
        example=3,
    )

    enabled: Optional[bool] = Query(
        None,
        description="Filter by enabled/disabled microcontrollers",
        example=True,
    )

    type: Optional[MicrocontrollerType] = Query(
        None,
        description="Filter by microcontroller type",
        example=MicrocontrollerType.RASPBERRY_PI_ZERO,
    )
