from pydantic import Field, IPvAnyAddress

from smart_common.schemas.base import APIModel


class FroniusProviderConfig(APIModel):
    host: IPvAnyAddress = Field(
        ...,
        description="Fronius inverter IP address (local network)",
    )

    use_https: bool = Field(
        default=False,
        description="Use HTTPS instead of HTTP",
    )

    max_power_kw: float = Field(
        default=20.0,
        gt=0,
        description="Maximum inverter power in kW",
    )
