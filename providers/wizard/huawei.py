# smart_common/providers/wizard/huawei.py
from __future__ import annotations

from typing import Any, Mapping

from smart_common.providers.adapter_factory import get_vendor_adapter_factory
from smart_common.providers.adapters.huawei_adapter import HuaweiProviderAdapter
from smart_common.providers.enums import ProviderVendor
from smart_common.providers.wizard.exceptions import WizardSessionStateError
from smart_common.providers.wizard.steps import WizardHandlerResult, WizardStep
from smart_common.schemas.provider_wizard.huawei import (
    HuaweiAuthStep,
    HuaweiDeviceStep,
    HuaweiStationStep,
)


# ---------------------------------------------------------------------
# STEP 1: AUTH
# ---------------------------------------------------------------------
def _auth_step(
    payload: HuaweiAuthStep,
    session_data: Mapping[str, Any],
) -> WizardHandlerResult:
    adapter = get_vendor_adapter_factory().create(
        ProviderVendor.HUAWEI,
        credentials={
            "username": payload.username,
            "password": payload.password,
        },
        cache_key=payload.username,
    )

    stations = adapter.list_stations()

    return {
        "next_step": "station",
        "options": {
            "stations": [
                {
                    "value": station["station_code"],
                    "label": station["name"],
                }
                for station in stations
            ]
        },
        "session_updates": {
            "credentials": {
                "username": payload.username,
                "password": payload.password,
            }
        },
    }


# ---------------------------------------------------------------------
# INTERNAL: resolve adapter from session
# ---------------------------------------------------------------------
def _resolve_adapter(session_data: Mapping[str, Any]) -> HuaweiProviderAdapter:
    credentials = session_data.get("credentials")
    if not credentials:
        raise WizardSessionStateError("Missing Huawei credentials in wizard session")

    overrides = session_data.get("adapter_overrides") or {}

    username = credentials.get("username")
    if not username:
        raise WizardSessionStateError("Missing username in wizard session credentials")

    return get_vendor_adapter_factory().create(
        ProviderVendor.HUAWEI,
        credentials=credentials,
        cache_key=username,
        overrides=overrides,
    )


# ---------------------------------------------------------------------
# STEP 2: STATION
# ---------------------------------------------------------------------
def _station_step(
    payload: HuaweiStationStep,
    session_data: Mapping[str, Any],
) -> WizardHandlerResult:
    adapter = _resolve_adapter(session_data)
    devices = adapter.list_devices(payload.station_code)

    return {
        "next_step": "device",
        "options": {
            "devices": [
                {
                    "value": device["device_id"],
                    "label": device["name"],
                }
                for device in devices
            ]
        },
        "session_updates": {
            "station_code": payload.station_code,
        },
        "context": {
            "station_code": payload.station_code,
        },
    }


# ---------------------------------------------------------------------
# STEP 3: DEVICE (FINAL)
# ---------------------------------------------------------------------
def _device_step(
    payload: HuaweiDeviceStep,
    session_data: Mapping[str, Any],
) -> WizardHandlerResult:
    credentials = session_data.get("credentials")
    if not credentials:
        raise WizardSessionStateError("Missing Huawei credentials in wizard session")

    station_code = payload.station_code or session_data.get("station_code")
    if not station_code:
        raise WizardSessionStateError("Missing station_code in wizard session")

    final_config = {
        "station_code": station_code,
        "device_id": payload.device_id,
        "max_power_kw": 20.0,
        "min_power_kw": 0.0,
    }

    return {
        "is_complete": True,
        "next_step": None,
        "final_config": final_config,
        "credentials": credentials,
        "session_updates": {
            "device_id": payload.device_id,
        },
        "context": {
            "device_id": payload.device_id,
        },
    }


# ---------------------------------------------------------------------
# WIZARD DEFINITION
# ---------------------------------------------------------------------
HUAWEI_WIZARD = {
    "auth": WizardStep(schema=HuaweiAuthStep, handler=_auth_step),
    "station": WizardStep(schema=HuaweiStationStep, handler=_station_step),
    "device": WizardStep(schema=HuaweiDeviceStep, handler=_device_step),
}
