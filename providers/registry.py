# smart_common/providers/registry.py
from __future__ import annotations

from typing import Any, Mapping

from smart_common.enums.unit import PowerUnit
from smart_common.providers.provider_config.config import provider_settings
from smart_common.providers.adapters.huawei_adapter import HuaweiProviderAdapter
from smart_common.enums.sensor import SensorType
from smart_common.providers.enums import ProviderKind, ProviderType, ProviderVendor
from smart_common.providers.provider_config.fronius import FroniusProviderConfig
from smart_common.providers.provider_config.goodwe import GoodWeProviderConfig
from smart_common.providers.provider_config.growatt import GrowattProviderConfig
from smart_common.providers.provider_config.huawei.final import HuaweiProviderConfig
from smart_common.providers.provider_config.credentials import UsernamePasswordCredentials
from smart_common.providers.provider_config.sensor_base import SensorThresholdConfig
from smart_common.providers.provider_config.sma import SMAProviderConfig
from smart_common.providers.provider_config.solaredge import SolarEdgeProviderConfig
from smart_common.providers.provider_config.victron import VictronProviderConfig
from smart_common.providers.wizard.huawei import HUAWEI_WIZARD


ProviderDefinition = Mapping[str, Any]


PROVIDER_DEFINITIONS: Mapping[ProviderVendor, ProviderDefinition] = {
    ProviderVendor.HUAWEI: {
        "label": "Huawei FusionSolar",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": PowerUnit.KILOWATT,
        "requires_wizard": True,
        "wizard_start": "auth",
        "config_schema": HuaweiProviderConfig,
        "credentials_schema": UsernamePasswordCredentials,
        "adapter": HuaweiProviderAdapter,
        "adapter_settings": {
            "base_url": provider_settings.HUAWEI_BASE_URL,
            "timeout": provider_settings.HUAWEI_TIMEOUT,
            "max_retries": provider_settings.HUAWEI_MAX_RETRIES,
        },
        "wizard": HUAWEI_WIZARD,
    },
    ProviderVendor.GOODWE: {
        "label": "GoodWe SEMS",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": PowerUnit.KILOWATT,
        "requires_wizard": False,
        "config_schema": GoodWeProviderConfig,
        "adapter": None,
        "wizard": None,
    },
    # ProviderVendor.SOLAREDGE: {
    #     "label": "SolarEdge",
    #     "provider_type": ProviderType.API,
    #     "kind": ProviderKind.POWER,
    #     "default_unit": "kW",
    #     "requires_wizard": False,
    #     "config_schema": SolarEdgeProviderConfig,
    #     "adapter": None,
    #     "wizard": None,
    # },
    # ProviderVendor.FRONIUS: {
    #     "label": "Fronius (Local API)",
    #     "provider_type": ProviderType.API,
    #     "kind": ProviderKind.POWER,
    #     "default_unit": "kW",
    #     "requires_wizard": False,
    #     "config_schema": FroniusProviderConfig,
    #     "adapter": None,
    #     "wizard": None,
    # },
    # ProviderVendor.VICTRON: {
    #     "label": "Victron Energy",
    #     "provider_type": ProviderType.API,
    #     "kind": ProviderKind.POWER,
    #     "default_unit": "kW",
    #     "requires_wizard": False,
    #     "config_schema": VictronProviderConfig,
    #     "adapter": None,
    #     "wizard": None,
    # },
    # ProviderVendor.GROWATT: {
    #     "label": "Growatt ShineServer",
    #     "provider_type": ProviderType.API,
    #     "kind": ProviderKind.POWER,
    #     "default_unit": "kW",
    #     "requires_wizard": True,
    #     "config_schema": GrowattProviderConfig,
    #     "adapter": None,
    #     "wizard": None,
    # },
    # ProviderVendor.SMA: {
    #     "label": "SMA Sunny Portal",
    #     "provider_type": ProviderType.API,
    #     "kind": ProviderKind.POWER,
    #     "default_unit": "kW",
    #     "requires_wizard": True,
    #     "config_schema": SMAProviderConfig,
    #     "adapter": None,
    #     "wizard": None,
    # },
    ProviderVendor.DHT22: {
        "label": "DHT22 Sensor",
        "provider_type": ProviderType.SENSOR,
        "kind": ProviderKind.TEMPERATURE,
        "default_unit": PowerUnit.CELSIUS,
        "requires_wizard": False,
        "config_schema": SensorThresholdConfig,
        "adapter": None,
        "wizard": None,
    },
    ProviderVendor.BME280: {
        "label": "BME280 Sensor",
        "provider_type": ProviderType.SENSOR,
        "kind": ProviderKind.TEMPERATURE,
        "default_unit": PowerUnit.CELSIUS,
        "requires_wizard": False,
        "config_schema": SensorThresholdConfig,
        "adapter": None,
        "wizard": None,
    },
    ProviderVendor.BH1750: {
        "label": "BH1750 Light Sensor",
        "provider_type": ProviderType.SENSOR,
        "kind": ProviderKind.LIGHT,
        "default_unit": PowerUnit.LUX,
        "requires_wizard": False,
        "config_schema": SensorThresholdConfig,
        "adapter": None,
        "wizard": None,
    },
}


def resolve_sensor_type(vendor: ProviderVendor) -> SensorType | None:
    """Return SensorType if the vendor refers to hardware, otherwise None."""
    try:
        return SensorType(vendor.value)
    except ValueError:
        return None
