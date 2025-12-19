from pydantic import Field

from smart_common.schemas.base import APIModel


class GrowattProviderConfig(APIModel):
    username: str = Field(..., description="Growatt ShineServer username")
    password: str = Field(..., description="Growatt ShineServer password")

    plant_id: str = Field(
        ...,
        description="Growatt plant ID",
    )

    inverter_sn: str | None = Field(
        None,
        description="Inverter serial number",
    )

    max_power_kw: float = Field(
        default=20.0,
        gt=0,
        description="Maximum inverter power in kW",
    )
