# smart_common/providers/provider_config/huawei/final.py
from pydantic import Field
from smart_common.schemas.base import APIModel


class HuaweiProviderConfig(APIModel):
    station_code: str
    device_id: str
    max_power_kw: float = Field(default=20.0, gt=0)
    min_power_kw: float = Field(default=0.0, ge=0)
