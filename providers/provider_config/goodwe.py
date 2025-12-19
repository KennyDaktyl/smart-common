from pydantic import Field

from smart_common.schemas.base import APIModel


class GoodWeProviderConfig(APIModel):
    username: str = Field(..., description="GoodWe SEMS username")
    password: str = Field(..., description="GoodWe SEMS password")

    station_id: str = Field(
        ...,
        description="GoodWe power station ID",
    )

    inverter_sn: str | None = Field(
        None,
        description="Inverter serial number (optional)",
    )

    max_power_kw: float = Field(
        default=20.0,
        gt=0,
        description="Maximum inverter power in kW",
    )
