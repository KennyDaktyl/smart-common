from __future__ import annotations

import logging
from inspect import Parameter, signature
from typing import Any, Mapping, Tuple

from smart_common.providers.base.provider_adapter import BaseProviderAdapter
from smart_common.providers.enums import ProviderVendor
from smart_common.providers.exceptions import ProviderNotSupportedError

logger = logging.getLogger(__name__)

_ADAPTER_CACHE: dict[Tuple[ProviderVendor, str], BaseProviderAdapter] = {}


class VendorAdapterFactory:
    """Creates and caches provider adapters based on registry metadata."""

    def __init__(
        self,
        provider_definitions: Mapping[ProviderVendor, Mapping[str, Any]],
    ) -> None:
        self._definitions = provider_definitions

    def create(
        self,
        vendor: ProviderVendor,
        *,
        credentials: Mapping[str, Any],
        cache_key: str,
        overrides: Mapping[str, Any] | None = None,
    ) -> BaseProviderAdapter:
        """
        Create or return cached adapter instance.

        cache_key:
            Unique identifier for adapter lifetime (e.g. username, user_id).
        """

        cache_id = (vendor, cache_key)

        cached = _ADAPTER_CACHE.get(cache_id)
        if cached:
            logger.debug(
                "Using cached provider adapter",
                extra={
                    "vendor": vendor.value,
                    "cache_key": cache_key,
                    "adapter": type(cached).__name__,
                },
            )
            return cached

        meta = self._definitions.get(vendor)
        if not meta:
            raise ProviderNotSupportedError(vendor.value)

        adapter_cls = meta.get("adapter")
        if not adapter_cls:
            raise ProviderNotSupportedError(vendor.value)

        if not issubclass(adapter_cls, BaseProviderAdapter):
            raise TypeError(
                f"Adapter {adapter_cls.__name__} must extend BaseProviderAdapter"
            )

        logger.info(
            "Creating provider adapter",
            extra={
                "vendor": vendor.value,
                "adapter_cls": adapter_cls.__name__,
                "cache_key": cache_key,
            },
        )

        adapter_settings = dict(meta.get("adapter_settings", {}))
        if overrides:
            adapter_settings.update(overrides)

        # ------------------------------------------------------------------
        # Filter adapter_settings by __init__ signature
        # ------------------------------------------------------------------
        init_sig = signature(adapter_cls.__init__)

        allowed_params = {
            name
            for name, param in init_sig.parameters.items()
            if name != "self"
            and param.kind
            in (
                Parameter.POSITIONAL_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
                Parameter.KEYWORD_ONLY,
            )
        }

        has_var_keyword = any(
            param.kind == Parameter.VAR_KEYWORD
            for param in init_sig.parameters.values()
        )

        if has_var_keyword:
            effective_settings = adapter_settings
        else:
            effective_settings = {
                k: v for k, v in adapter_settings.items() if k in allowed_params
            }

        try:
            adapter = adapter_cls(**credentials, **effective_settings)
        except TypeError as exc:
            logger.exception(
                "Failed to instantiate provider adapter",
                extra={
                    "vendor": vendor.value,
                    "adapter_cls": adapter_cls.__name__,
                    "credentials": list(credentials.keys()),
                    "settings": list(effective_settings.keys()),
                },
            )
            raise

        _ADAPTER_CACHE[cache_id] = adapter
        return adapter

    # ------------------------------------------------------------------
    # Cache utilities
    # ------------------------------------------------------------------
    def clear_cache(self) -> None:
        _ADAPTER_CACHE.clear()
        logger.warning("Provider adapter cache cleared")


def get_vendor_adapter_factory() -> VendorAdapterFactory:
    from smart_common.providers.registry import PROVIDER_DEFINITIONS

    return VendorAdapterFactory(PROVIDER_DEFINITIONS)
