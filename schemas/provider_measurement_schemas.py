from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderMeasurementResponse(BaseModel):
    id: int
    measured_at: datetime
    measured_value: Optional[float]
    measured_unit: Optional[str]
    metadata_payload: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
