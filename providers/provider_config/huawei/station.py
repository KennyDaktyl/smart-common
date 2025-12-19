# smart_common/providers/provider_config/huawei/station.py
from pydantic import Field
from smart_common.schemas.base import APIModel


class HuaweiStationStep(APIModel):
    station_code: str = Field(..., description="Huawei station code")
