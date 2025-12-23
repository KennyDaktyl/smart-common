from __future__ import annotations

from pydantic import Field

from smart_common.schemas.base import APIModel


class HuaweiAuthStep(APIModel):
    username: str = Field(..., min_length=1, description="FusionSolar user login")
    password: str = Field(..., min_length=1, description="FusionSolar password")


class HuaweiStationStep(APIModel):
    station_code: str = Field(..., description="Selected station identifier")


class HuaweiDeviceStep(APIModel):
    station_code: str = Field(..., description="Station identifier (hidden)")
    device_id: str = Field(..., description="Device identifier selected by user")
