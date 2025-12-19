from pydantic import Field

from smart_common.schemas.base import APIModel


class SMAProviderConfig(APIModel):
    client_id: str = Field(..., description="SMA OAuth client id")
    client_secret: str = Field(..., description="SMA OAuth client secret")

    system_id: str = Field(
        ...,
        description="SMA system / plant ID",
    )

    max_power_kw: float = Field(
        default=20.0,
        gt=0,
        description="Maximum inverter power in kW",
    )
