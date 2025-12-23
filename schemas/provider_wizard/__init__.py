from __future__ import annotations

from smart_common.providers.enums import ProviderVendor
from smart_common.schemas.base import APIModel


class WizardRuntimeResponse(APIModel):
    vendor: ProviderVendor
    step: str | None
    schema: dict | None
    options: dict
    context: dict
    is_complete: bool
    final_config: dict | None = None
