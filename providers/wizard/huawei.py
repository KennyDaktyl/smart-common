from smart_common.providers.wizard.steps import WizardStep
from smart_common.schemas.provider_wizard.huawei import (
    HuaweiAuthStep,
    HuaweiStationStep,
)
from smart_common.providers.adapters.huawei_adapter import HuaweiAdapter


def auth_step(payload: HuaweiAuthStep):
    adapter = HuaweiAdapter(payload.username, payload.password)
    stations = adapter.get_stations()

    return {
        "next_step": "station",
        "options": {
            "stations": [
                {
                    "value": s["stationCode"],
                    "label": s["stationName"],
                }
                for s in stations
            ]
        },
    }


def station_step(payload: HuaweiStationStep):
    adapter = HuaweiAdapter(payload.username, payload.password)
    devices = adapter.get_devices_for_station(payload.station_code)

    return {
        "next_step": "device",
        "options": {
            "devices": [
                {
                    "value": d["devId"],
                    "label": d["devName"],
                }
                for d in devices
            ]
        },
    }


HUAWEI_WIZARD = {
    "auth": WizardStep(
        schema=HuaweiAuthStep,
        handler=auth_step,
    ),
    "station": WizardStep(
        schema=HuaweiStationStep,
        handler=station_step,
    ),
}
