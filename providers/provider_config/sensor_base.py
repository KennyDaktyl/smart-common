from pydantic import BaseModel, Field

from smart_common.enums.unit import PowerUnit


class SensorThresholdConfig(BaseModel):
    min_value: float | None = Field(None, description="Minimum acceptable value")
    max_value: float | None = Field(None, description="Maximum acceptable value")
    unit: PowerUnit = Field(
        ...,
        description="Measurement unit",
    )
