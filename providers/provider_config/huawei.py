from pydantic import Field

from smart_common.schemas.base import APIModel


class HuaweiProviderConfig(APIModel):
    # ---------- auth ----------
    username: str = Field(..., description="Huawei FusionSolar username")
    password: str = Field(..., description="Huawei FusionSolar password")

    # ---------- installation ----------
    station_code: str = Field(..., description="Huawei station code")
    device_id: str = Field(..., description="Huawei inverter device id")

    # ---------- physical characteristics ----------
    max_power_kw: float = Field(
        default=20.0,
        description="Maximum inverter power in kW",
        gt=0,
    )
