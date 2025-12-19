from smart_common.providers.enums import ProviderKind, ProviderType, ProviderVendor
from smart_common.providers.provider_config.fronius import FroniusProviderConfig
from smart_common.providers.provider_config.goodwe import GoodWeProviderConfig
from smart_common.providers.provider_config.growatt import GrowattProviderConfig
from smart_common.providers.provider_config.huawei import HuaweiProviderConfig
from smart_common.providers.provider_config.sma import SMAProviderConfig
from smart_common.providers.provider_config.solaredge import SolarEdgeProviderConfig
from smart_common.providers.provider_config.victron import VictronProviderConfig

PROVIDER_DEFINITIONS = {
    ProviderVendor.HUAWEI: {
        "label": "Huawei FusionSolar",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": True,
        "config_schema": HuaweiProviderConfig,
    },
    ProviderVendor.GOODWE: {
        "label": "GoodWe SEMS",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": True,
        "config_schema": GoodWeProviderConfig,
    },
    ProviderVendor.SOLAREDGE: {
        "label": "SolarEdge",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": False,
        "config_schema": SolarEdgeProviderConfig,
    },
    ProviderVendor.FRONIUS: {
        "label": "Fronius (Local API)",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": False,
        "config_schema": FroniusProviderConfig,
    },
    ProviderVendor.VICTRON: {
        "label": "Victron Energy",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": False,
        "config_schema": VictronProviderConfig,
    },
    ProviderVendor.GROWATT: {
        "label": "Growatt ShineServer",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": True,
        "config_schema": GrowattProviderConfig,
    },
    ProviderVendor.SMA: {
        "label": "SMA Sunny Portal",
        "provider_type": ProviderType.API,
        "kind": ProviderKind.POWER,
        "default_unit": "kW",
        "requires_wizard": True,
        "config_schema": SMAProviderConfig,
    },
}
