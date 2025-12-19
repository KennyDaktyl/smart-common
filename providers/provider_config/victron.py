from pydantic import Field

from smart_common.schemas.base import APIModel


class VictronProviderConfig(APIModel):
    api_token: str = Field(..., description="Victron VRM API token")

    installation_id: str = Field(
        ...,
        description="Victron installation ID",
    )

    max_power_kw: float = Field(
        default=20.0,
        gt=0,
        description="Maximum inverter power in kW",
    )
