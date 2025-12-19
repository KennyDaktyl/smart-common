from typing import Any, Dict, List

from pydantic import Field

from smart_common.providers.enums import ProviderKind, ProviderType, ProviderVendor
from smart_common.schemas.base import APIModel

# -------------------------
# Vendor w liście
# -------------------------


class ProviderVendorSummary(APIModel):
    vendor: ProviderVendor = Field(..., description="Provider vendor")
    label: str = Field(..., description="Human readable vendor name")
    kind: ProviderKind = Field(..., description="Measurement domain")
    default_unit: str = Field(..., description="Default measurement unit")
    requires_wizard: bool = Field(..., description="Whether wizard flow is required")


# -------------------------
# Typ providera (API / SENSOR)
# -------------------------


class ProviderTypeDefinition(APIModel):
    type: ProviderType = Field(..., description="Provider type")
    vendors: List[ProviderVendorSummary]


# -------------------------
# GET /providers/definitions
# -------------------------


class ProviderDefinitionsResponse(APIModel):
    provider_types: List[ProviderTypeDefinition]


# -------------------------
# GET /providers/definitions/{vendor}
# -------------------------


class ProviderDefinitionDetail(APIModel):
    vendor: ProviderVendor
    label: str
    provider_type: ProviderType
    kind: ProviderKind
    default_unit: str
    requires_wizard: bool
    config_schema: Dict[str, Any] = Field(
        ...,
        description="JSON Schema for provider configuration",
    )
