from smart_common.providers.adapters.base import BaseProviderAdapter


class HuaweiProviderAdapter(BaseProviderAdapter):
    def __init__(self, username: str, password: str):
        super().__init__(username=username, password=password)
        self._adapter = LegacyHuaweiAdapter(username, password)

    def connect(self) -> None:
        # login happens lazily in _ensure_login
        pass

    def list_stations(self) -> list[dict]:
        return self._adapter.get_stations()

    def list_devices(self, station_code: str) -> list[dict]:
        return self._adapter.get_devices_for_station(station_code)

    def get_current_power(self, device_id: str) -> float:
        data = self._adapter.get_production(device_id)
        # ⬇️ normalizacja
        return float(data[0]["dataItemMap"]["active_power"])
