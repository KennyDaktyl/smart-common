from typing import Any, Dict

from pydantic import Field

from schemas.base import APIModel, ORMModel


class ProviderBase(APIModel):
    name: str
    provider_type: str
    vendor: str
    unit: str
    polling_interval_sec: int = Field(gt=0)
    config: Dict[str, Any]
    login: str | None = None
    password: str | None = None


class ProviderOut(ProviderBase, ORMModel):
    id: int
    uuid: str
    installation_id: int
    enabled: bool
    last_value: float | None = None
