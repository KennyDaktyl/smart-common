from abc import ABC, abstractmethod
from typing import Any


class BaseProviderAdapter(ABC):

    def __init__(self, **credentials: Any):
        self.credentials = credentials

    # ---------- lifecycle ----------

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    # ---------- discovery ----------

    def list_stations(self) -> list[dict]:
        raise NotImplementedError

    def list_devices(self, station_code: str) -> list[dict]:
        raise NotImplementedError

    # ---------- measurements ----------

    @abstractmethod
    def get_current_power(self, device_id: str) -> float:
        raise NotImplementedError
