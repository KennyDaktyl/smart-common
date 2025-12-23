from typing import Dict, Tuple
from smart_common.providers.base.provider_adapter import BaseProviderAdapter
from smart_common.providers.enums import ProviderVendor

_adapter_cache: Dict[Tuple[ProviderVendor, str], BaseProviderAdapter] = {}


def get_cached_adapter(
    vendor: ProviderVendor,
    *,
    cache_key: str,
    factory,
):
    key = (vendor, cache_key)
    adapter = _adapter_cache.get(key)
    if adapter:
        return adapter

    adapter = factory()
    _adapter_cache[key] = adapter
    return adapter
