from pydantic import Field

from smart_common.schemas.base import APIModel


class SolarEdgeProviderConfig(APIModel):
    api_key: str = Field(..., description="SolarEdge API key")

    site_id: str = Field(
        ...,
        description="SolarEdge site ID",
    )

    inverter_id: str | None = Field(
        None,
        description="Specific inverter ID (optional)",
    )

    max_power_kw: float = Field(
        default=20.0,
        gt=0,
        description="Maximum inverter power in kW",
    )
